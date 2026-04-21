import cv2
import os
import dlib
import numpy as np
from scipy.spatial import distance
from dotenv import load_dotenv

load_dotenv()

USE_MINIVISION = os.getenv("USE_MINIVISION", "False").lower() == "true"

if USE_MINIVISION:
    from app.core.antispoof_detector import AntiSpoofDetector


class LivenessDetector:
    def __init__(self, model_path: str = "models/shape_predictor_68_face_landmarks.dat"):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(model_path)

        if USE_MINIVISION:
            self.antispoof = AntiSpoofDetector()
            print("✅ MiniVision anti-spoof enabled")
        else:
            self.antispoof = None
            print("⚠️  MiniVision anti-spoof disabled (using basic checks only)")

        self.LEFT_EYE = list(range(42, 48))
        self.RIGHT_EYE = list(range(36, 42))
        
        self.EAR_THRESHOLD = 0.25   
        self.BLINK_FRAMES = 2       
        
        self.closed_frames = 0
        self.blink_count = 0

    def get_ear(self, eye_points: np.ndarray) -> float:
        """
        Calculate Eye Aspect Ratio
        
        EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
        
        p1-p6 are the 6 eye landmark points
        """

        A = distance.euclidean(eye_points[1], eye_points[5])
        B = distance.euclidean(eye_points[2], eye_points[4])
        

        C = distance.euclidean(eye_points[0], eye_points[3])
        
        ear = (A + B) / (2.0 * C)
        return ear

    def get_eye_points(self, landmarks, eye_indices: list) -> np.ndarray:
        """Extract eye landmark coordinates"""
        return np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in eye_indices])

    def reset(self):
        """Reset blink counter - call this before each student"""
        self.closed_frames = 0
        self.blink_count = 0

    def process_frame(self, frame: np.ndarray) -> dict:
        """
        Process a single frame and detect blinks
        
        Returns:
            dict with ear, blink_count, eye_closed, face_found
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)

        if len(faces) == 0:
            return {"face_found": False, "ear": 0.0, "blink_count": self.blink_count, "eye_closed": False}

        landmarks = self.predictor(gray, faces[0])

        left_eye = self.get_eye_points(landmarks, self.LEFT_EYE)
        right_eye = self.get_eye_points(landmarks, self.RIGHT_EYE)

        left_ear = self.get_ear(left_eye)
        right_ear = self.get_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0

        eye_closed = avg_ear < self.EAR_THRESHOLD

        if eye_closed:
            self.closed_frames += 1
        else:
            if self.closed_frames >= self.BLINK_FRAMES:
                self.blink_count += 1
            self.closed_frames = 0

        return {
            "face_found": True,
            "ear": avg_ear,
            "eye_closed": eye_closed,
            "blink_count": self.blink_count
        }

    def wait_for_blink(self, cap, required_blinks: int = 1, timeout_seconds: int = 10) -> dict:
        """
        Wait for student to blink required number of times
        
        Args:
            cap: OpenCV camera capture
            required_blinks: How many blinks needed
            timeout_seconds: Give up after this many seconds
            
        Returns:
            True if blinked, False if timeout
        """
        import time
        self.reset()
        start_time = time.time()

        collected_frames = []

        print(f"Waiting for {required_blinks} blink(s)...")

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                print("Timeout - no blink detected")
                return {"success": False, "reason": "timeout"}

            ret, frame = cap.read()
            if not ret:
                return {"success": False, "reason": " not ret"}
            
            if len(collected_frames) <10:
                collected_frames.append(frame.copy())

            result = self.process_frame(frame)

            ear_text = f"EAR: {result['ear']:.2f}"
            blink_text = f"Blinks: {result['blink_count']}/{required_blinks}"
            status = "Blink Please!" if not result['eye_closed'] else "..."

            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, ear_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(frame, blink_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(frame, f"Time: {int(timeout_seconds - elapsed)}s", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.imshow('Liveness Check', frame)
            cv2.waitKey(1)

            if result['blink_count'] >= required_blinks:
                print(f"Blink detected!")

                if self.antispoof is not None:
                    print("Running MiniVision anti-spoof check...")
                    
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.detector(gray)
                    
                    if len(faces) == 0:
                        return {"success": False, "reason": "no_face_for_spoof"}
                    
                    face = faces[0]
                    bbox = [face.left(), face.top(), face.right(), face.bottom()]
                    
                    spoof = self.antispoof.check(frame, bbox)
                    
                    if not spoof["is_real"]:
                        print(f"Spoof detected! Score: {spoof['score']:.2f}")
                        return {"success": False, "reason": "spoof", "score": spoof["score"]}
                    
                    print(f"Real face confirmed (score: {spoof['score']:.2f})")
                    return {"success": True, "method": "minivision", "score": spoof["score"]}
                else:
                    print("Liveness passed (basic checks only)")
                    return {"success": True, "method": "basic"}