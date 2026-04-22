import cv2
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.face_recognition import FaceRecognitionEngine
from app.database.database import sessionLocal
from app.database.models import Teacher


def enroll_teachers_from_photos(photos_dir: str = "data/teacher_photos"):

    print(f"Looking in {photos_dir}")

    engine = FaceRecognitionEngine()
    engine.load_model()

    db = sessionLocal()

    teacher_folders = sorted(os.listdir(photos_dir))
    print(f"Found folders: {teacher_folders}")

    for folder_name in teacher_folders:
        folder_path = os.path.join(photos_dir, folder_name)

        print(f"\nProcessing: {folder_path}")

        if not os.path.isdir(folder_path):
            print(f"Skipping: {folder_path} - not a folder")
            continue

        # Expected format: T001_JohnDoe
        parts = folder_name.split("_", 1)
        teacher_id = parts[0]
        teacher_name = parts[1] if len(parts) > 1 else folder_name

        print(f"Enrolling {teacher_name} (ID: {teacher_id})...")

        # Prevent duplicate
        existing = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
        if existing:
            print(f"Skipping {teacher_id} - already exists")
            continue

        embeddings = []

        photos = os.listdir(folder_path)
        print(f"Photos found: {photos}")

        for photo_file in photos:
            print(f"Checking file: {photo_file}")

            if not photo_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                print(f"Skipping {photo_file} - not an image")
                continue

            photo_path = os.path.join(folder_path, photo_file)
            image = cv2.imread(photo_path)

            if image is None:
                print(f"Could not read {photo_file}")
                continue

            print(f"Generating embedding for {photo_file}...")
            embedding = engine.generate_embedding(image)

            if embedding is not None:
                embeddings.append(embedding.tolist())  # JSON compatible
                print(f"Done {photo_file}")
            else:
                print(f"No face in {photo_file}")

        if len(embeddings) == 0:
            print(f"No valid embeddings for {teacher_name}")
            continue

        # Save to DB
        teacher = Teacher(
            teacher_id=teacher_id,
            name=teacher_name,
            email=None,        # optional for now
            phone=None,
            department=None,
            face_embeddings=embeddings
        )

        db.add(teacher)
        db.commit()

        print(f"Enrolled {teacher_name} with {len(embeddings)} embeddings")

    db.close()
    print("\nDone enrolling all teachers")


if __name__ == "__main__":
    enroll_teachers_from_photos()