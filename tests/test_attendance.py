
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from app.core.face_recognition import FaceRecognitionEngine
from app.core.attendance_engine import AttendanceEngine
from app.database.database import sessionLocal
from app.core.liveness_detection import LivenessDetector
from app.core.quality_check import QualityChecker

# Initialize
db = sessionLocal()
face_engine = FaceRecognitionEngine()
liveness = LivenessDetector()
face_engine.load_model()
face_engine.load_student_embeddings()
quality = QualityChecker()

attendance = AttendanceEngine(db)

# Start a test session
attendance.start_session(
    session_name="Test Session",
    class_name="EEIOT3",
    total_students=4
)

cap = cv2.VideoCapture(0)
print("\nPress SPACE to mark attendance, Q to quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow('Attendance Test - Press SPACE', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord(' '):
        print("\n=== starting attendance process ===")

        print("1. Checking image quality...")
        quality_result = quality.check_all(frame)
        if not quality_result["passed"]:
            print(f"❌ Quality check failed:")
            for failure in quality_result["failures"]:
                print(f"   - {failure}")
            continue
        print("✅ Quality check passed")


        print("2. Detecting face...")
        student_id, student_name, confidence = face_engine.recognize_face(frame)

        if not student_id:
            print(f"Face not recognized ({confidence:.2%})")

        print(f"Recognized {student_name} ({confidence:.2%})")

        if attendance.check_already_marked(student_id):
            print(f"{student_name} already marked present")
            continue

        print("3. Checking liveness - BLINK THRICE")
        blink_passed = liveness.wait_for_blink(cap, required_blinks=3, timeout_seconds=10)

        if not blink_passed:
            print("Liveness check failed - no blink detected")
            cv2.destroyWindow('Liveness Check')
            continue
        
        cv2.destroyWindow('Liveness Check')
        print("Liveness check passed")

        print("4. Marking attendance...")
        result = attendance.mark_attendance(student_id, student_name, confidence)

        if result["success"]:
            print(f"{result['student_name']} marked present")
            print(f"   Present: {result['present_count']}/{result['total']}")

        else:
            print(f"{result['message']}")


        print("=== process complete ==\n")
            
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# End session
stats = attendance.end_session()
print(f"\n Session ended")
print(f"Present: {stats['present']}/{stats['total']}")
print(f"Rate: {stats['rate']}%")

db.close()
