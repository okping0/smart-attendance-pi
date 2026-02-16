import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
from app.database.database import sessionLocal
from app.database.models import Student

def sync():
    # Load embeddings
    with open("data/embeddings.pkl", "rb") as f:
        data = pickle.load(f)

    db = sessionLocal()

    count = 0
    for student_id, info in data.items():
        # Check if already in database
        existing = db.query(Student).filter(Student.student_id == student_id).first()

        if existing:
            print(f"⚠️  {info['name']} already in database, skipping")
            continue

        # Convert numpy arrays to lists (JSON serializable)
        embeddings_as_lists = [e.tolist() for e in info["embeddings"]]

        student = Student(
            student_id=student_id,
            name=info["name"],
            face_embeddings=embeddings_as_lists
        )

        db.add(student)
        count += 1
        print(f"✅ Added {info['name']} (ID: {student_id})")

    db.commit()
    db.close()

    print(f"\n✅ Synced {count} students to database")

if __name__ == "__main__":
    sync()