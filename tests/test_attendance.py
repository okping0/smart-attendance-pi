import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from app.core.face_recognition import FaceRecognitionEngine
from app.core.attendance_engine import AttendanceEngine
from app.database.database import sessionLocal

# Initialize
db = sessionLocal()
face_engine = FaceRecognitionEngine()
face_engine.load_model()
face_engine.load_student_embeddings()

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
        student_id, student_name, confidence = face_engine.recognize_face(frame)

        if student_id:
            result = attendance.mark_attendance(student_id, student_name, confidence)

            if result["success"]:
                print(f"✅ {result['student_name']} marked present ({confidence:.2%})")
                print(f"   Present: {result['present_count']}/{result['total']}")
            else:
                print(f"⚠️  {result['message']}")
        else:
            print(f"❌ Face not recognized ({confidence:.2%})")

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