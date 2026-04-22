from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import pickle, numpy as np, os

from app.database.models import Teacher

SIMILARITY_THRESHOLD = 0.45
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")


def create_token(data: dict) -> str:
    payload = {**data, "exp": datetime.utcnow() + timedelta(hours=8)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        return None


class TeacherAuthEngine:
    def __init__(self, db: Session):
        self.db = db

    def face_login(self, query_embedding: np.ndarray) -> Dict:
        if query_embedding is None:
            return {"success": False, "error": "NO_FACE", "message": "No face detected"}

        teachers = self.db.query(Teacher).all()

        if not teachers:
            return {"success": False, "error": "NO_TEACHERS", "message": "No teachers enrolled"}

        best_similarity, best_teacher = 0.0, None

        for teacher in teachers:
            stored = pickle.loads(teacher.embedding)
            similarity = float(
                np.dot(query_embedding, stored) /
                (np.linalg.norm(query_embedding) * np.linalg.norm(stored))
            )
            if similarity > best_similarity:
                best_similarity = similarity
                best_teacher    = teacher

        if best_similarity < SIMILARITY_THRESHOLD:
            return {"success": False, "error": "NOT_RECOGNIZED", "message": "Face not recognised"}

        print(f"Teacher login: {best_teacher.name} (similarity: {round(best_similarity, 4)})")
        return {
            "success":      True,
            "teacher_id":   best_teacher.id,
            "employee_id":  best_teacher.employee_id,
            "teacher_name": best_teacher.name,
            "logged_in_at": datetime.now()
        }