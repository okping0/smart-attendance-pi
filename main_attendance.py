import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from app.core.face_recognition import FaceRecognitionEngine
from app.core.attendance_engine import AttendanceEngine
from app.database.database import sessionLocal
from app.core.liveness_detection import LivenessDetector
from app.core.quality_check import QualityChecker

class AttendanceSystem:
  def __init__(self):
    print("Initializing attendance system...")

    self.db = sessionLocal()
    self.face_engine = FaceRecognitionEngine()
    self.liveness = LivenessDetector()
    self.quality = QualityChecker()
    self.attendance = AttendanceEngine(self.db)

    self.face_engine.load_model()
    self.face_engine.load_student_embeddings()

    self.max_retries = 3

    print("System ready")

  def process_student(self, frame, cap ) -> dict:
    """
    complete attendance process for one student
    returns result dict
    """

    # step 1- quality check
    quality_result = self.quality.check_all(frame)
    if not quality_result["passed"]:
      return {"success": False, "stage": "quality", "errors": quality_result["failures"]}
    
    # step2 - face recognition
    student_id, student_name, confidence = self.face_engine.recognize_face(frame)
    if not student_id:
      return{"success": False, "stage":"recognition", "confidence": confidence}
    
    # step 3- check duplicate
    if self.attendance.check_already_marked(student_id):
      return{"success": False, "stage": "duplicate", "student_name": student_name}
    
    # step-4 check liveness
    blink_passed = self.liveness.wait_for_blink(cap, required_blinks=3, timeout_seconds=10)
    cv2.destroyWindow('Liveness Check')

    if not blink_passed["success"]:
      reason = blink_passed.get("reason", "unknown")
      return {"success": False, "stage": "Liveness"}
    
    result = self.attendance.mark_attendance(student_id, student_name, confidence)

    if result["success"]:
      return{
        "success": True,
        "student_name": result["student_name"],
        "student_id": result["student_id"],
        "present_count": result["present_count"],
        "total": result["total"]
      }
    else:
      return{
        "success": False,
        "stage": "database",
        "message": result["message"]
      }
    
  def run(self):
        """Main loop"""
        # check if already a session..if not tell to create one 

        from app.database.models import Session as SessionModel

        active = self.db.query(SessionModel).filter(SessionModel.is_active == True).first()

        if active:
           print(f"using existing sesson: {active.session_name} (ID:{active.id} )")
           self.attendance.current_session_id = active.id

        else:
           print("No active session found. create one from the API first")
           return
        
        cap = cv2.VideoCapture(0)
        print("\n--- Press SPACE to mark attendance, Q to quit ---\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            cv2.imshow('Attendance System - Press SPACE', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' '):
                result = self.process_student(frame, cap)
                
                if result["success"]:
                    print(f"{result['student_name']} marked present!")
                    print(f"   Count: {result['present_count']}/{result['total']}\n")
                else:
                    stage = result["stage"]
                    if stage == "quality":
                        print(f"Quality check failed:")
                        for err in result["errors"]:
                            print(f"   - {err}")
                    elif stage == "recognition":
                        print(f"Face not recognized ({result['confidence']:.2%})")
                    elif stage == "duplicate":
                        print(f" {result['student_name']} already marked!")
                    elif stage == "liveness":
                        print(f"Liveness check failed - no blink detected")
                    elif stage == "database":
                        print(f"Database error: {result['message']}")
                    print()
            
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # End session
        stats = self.attendance.end_session()
        print(f"\n--- Session Complete ---")
        print(f"Present: {stats['present']}/{stats['total']}")
        print(f"Attendance Rate: {stats['rate']}%")
        
        self.db.close()

if __name__ == "__main__":
    system = AttendanceSystem()
    system.run()




    