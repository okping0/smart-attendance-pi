import cv2
import numpy as np

class ScreenDetector:
    def __init__(self):
        self.moire_threshold = 0.15
        self.color_temp_threshold = 1.15
        
    def detect_moire_pattern(self, frame: np.ndarray) -> dict:
        """
        Screens create moiré patterns (interference) when captured by cameras
        Real faces don't have this
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply FFT to detect periodic patterns
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)
        
        # Normalize
        magnitude = magnitude / magnitude.max()
        
        # Count high frequency peaks (moiré creates these)
        threshold = 0.3
        peaks = np.sum(magnitude > threshold)
        total_pixels = magnitude.size
        
        peak_ratio = peaks / total_pixels
        
        is_screen = peak_ratio > self.moire_threshold
        
        return {
            "is_screen": is_screen,
            "confidence": peak_ratio,
            "method": "moire"
        }
    
    def detect_color_temperature(self, frame: np.ndarray) -> dict:
        """
        Screens emit more blue light than natural faces
        """
        # Split into B, G, R channels
        b, g, r = cv2.split(frame)
        
        # Calculate average color temperature
        avg_blue = np.mean(b)
        avg_red = np.mean(r)
        
        # Blue/Red ratio (screens have higher ratio)
        if avg_red == 0:
            ratio = 0
        else:
            ratio = avg_blue / avg_red
        
        is_screen = ratio > self.color_temp_threshold
        
        return {
            "is_screen": is_screen,
            "confidence": ratio,
            "method": "color_temp"
        }
    
    def check_frame(self, frame: np.ndarray) -> dict:
        """
        Run both checks on a single frame
        """
        moire = self.detect_moire_pattern(frame)
        color_temp = self.detect_color_temperature(frame)
        
        # If either detects screen, flag it
        is_screen = moire["is_screen"] or color_temp["is_screen"]
        
        return {
            "is_screen": is_screen,
            "moire_check": moire,
            "color_temp_check": color_temp
        }
    
    def analyze_multiple_frames(self, frames: list) -> dict:
        """
        Analyze 5-10 frames for consensus
        More reliable than single frame
        """
        screen_count = 0
        
        for frame in frames:
            result = self.check_frame(frame)
            if result["is_screen"]:
                screen_count += 1
        
        # If majority say screen, it's a screen
        confidence = screen_count / len(frames)
        is_screen = confidence > 0.5
        
        return {
            "is_screen": is_screen,
            "confidence": confidence,
            "frames_analyzed": len(frames)
        }