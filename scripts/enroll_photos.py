import cv2
import numpy as np
import pickle
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.face_recognition import FaceRecognitionEngine

def enroll_from_photos(photos_dir: str = "data/students_photos"):

  #debug
  print(f"looking in {photos_dir}") 

  engine = FaceRecognitionEngine()
  engine.load_model()

  embeddings_file = "data/embeddings.pkl"
  if os.path.exists(embeddings_file):
    with open(embeddings_file, "rb") as f:
      all_embeddings = pickle.load(f)
  else:
    all_embeddings = {}

  student_folders = sorted(os.listdir(photos_dir))

  #debug
  print(f"found folders: {student_folders}")

  for folder_name in student_folders:
    folder_path = os.path.join(photos_dir, folder_name)

    #debug
    print(f"processing: {folder_path}")

    if not os.path.isdir(folder_path):

      #debug
      print(f"skipping: {folder_path} - not a folder")
      continue

    parts = folder_name.split("_", 1)
    student_id = parts[0]
    student_name = parts[1] if len(parts) > 1 else folder_name

    print(f"\nEnrolling {student_name} (ID: {student_id})...")

    embeddings =[]

    #debug
    photos =os.listdir(folder_path)
    print(f"photos found: {photos}")

    for photo_file in os.listdir(folder_path):

      #debug
      print(f"checking file: {photo_file}")

      if not photo_file.lower().endswith(('.jpg', '.jpeg', '.png')):
        #debug
        print(f"Skipping {photo_file} - not an image")
        continue

      photo_path = os.path.join(folder_path, photo_file)
      image = cv2.imread(photo_path)

      if image is None:
        print(f" Could not read {photo_file}")
        continue

      #debug
      print(f"Generating embedding for {photo_file}...")
      
      embedding = engine.generate_embedding(image)

      if embedding is not None:
        embeddings.append(embedding)
        print(f" done {photo_file}")

      else:
        print(f" No face in {photo_file}")

    if len(embeddings) > 0:
      all_embeddings[student_id] = {
        "name": student_name,
        "embeddings": embeddings
      }
      print(f"enrolled {student_name} with {len(embeddings)} photos")

  os.makedirs("data", exist_ok=True)
  with open(embeddings_file, "wb") as f:
    pickle.dump(all_embeddings, f)

  print(f"\n Done! Toatal enrolled: {len(all_embeddings)} students")

if __name__ == "__main__":
  enroll_from_photos()
