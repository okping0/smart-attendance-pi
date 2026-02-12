from app.core.face_recognition import FaceRecognitionEngine
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

engine = FaceRecognitionEngine()
engine.load_model()
engine.load_student_embeddings()

cap = cv2.VideoCapture(0)
print("Press SPACE to recognize, Q to quit")

while True:
  ret, frame = cap.read()
  if not ret:
    break

  faces = engine.app.get(frame)

  for face in faces:
    x1,y1,x2,y2 = [int(c) for c in face.bbox]

    best_id, best_name, best_score = engine.recognize_face(frame)

    if best_id:
      color = (0,255,0)
      label = f"{best_name}"
    else:
      color = (0,0,255)
      label = f"Unknown"

    cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)

    cv2.putText(frame, label, (x1,y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

  cv2.imshow('Recognition Test', frame)

  key = cv2.waitKey(1) & 0xFF

  if key == ord(' '):
    student_id, student_name, confidence = engine.recognize_face(frame)
    if student_id:
      print(f"{student_name} (ID: {student_id}) - {confidence:.2%}")
    else:
      print(f"Unknown - {confidence:.2%}")

  elif key == ord('q'):
    break

cap.release()
cv2.destroyAllWindows()