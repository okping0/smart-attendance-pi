import cv2
import numpy as np
from app.core.face_recognition import FaceRecognitionEngine
import pickle
import os

student_id = input("Student ID: ")
student_name = input("Student name: ")

engine = FaceRecognitionEngine()
engine.load_model()

cap = cv2.VideoCapture(0)
embeddings = []
count = 0
required = 5

print(f"\nCapture {required} photos - Press SPACE")

while count < required:
  ret, frame = cap.read()
  if not ret:
    break
  cv2.putText(frame, f"Photos: {count}/{required}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
  cv2.imshow('Enrollment', frame)

  if cv2.waitKey(1) & 0xFF == ord(' '):
    embedding = engine.generate_embedding(frame)
    if embedding is not None:
      embeddings.append(embedding)
      count += 1
      print(f"{count}/{required}")
    else:
      print("No face detected")

cap.release()
cv2.destroyAllWindows()

if len(embeddings) == required:
  os.makedirs("data", exist_ok=True)

  embeddings_file = "../data/embeddings.pkl"
  if os.path.exists(embeddings_file):
    with open(embeddings_file, 'rb') as f:
      all_embeddings = pickle.load(f)

  else:
    all_embeddings = {}

  all_embeddings[student_id] = {
    "name": student_name,
    "embeddings": embeddings
  }

  with open(embeddings_file, 'wb') as f:
    pickle.dump(all_embeddings, f)

  print(f"\n Enrolled {student_name} !")