import cv2
import numpy as np
from app.core.face_recognition import FaceRecognitionEngine
from app.database.database import sessionLocal
from app.database.models import Teacher
from datetime import datetime

class TeacherAuth:
    def __init__(self):
        self.engine = FaceRecognitionEngine()
        self.engine.load_model()
        self.threshold = 0.60
    
    def load_teacher_embeddings(self):
        """Load all teacher embeddings from database"""
        db = sessionLocal()
        teachers = db.query(Teacher).filter(Teacher.is_active == True).all()
        
        self.teacher_data = {}
        for teacher in teachers:
            self.teacher_data[teacher.teacher_id] = {
                "name": teacher.name,
                "embeddings": [np.array(emb) for emb in teacher.face_embeddings]
            }
        
        db.close()
        print(f"Loaded {len(self.teacher_data)} teachers")
    
    def authenticate(self, frame):
        """
        Authenticate teacher from face
        Returns: (teacher_id, name, confidence) or (None, None, 0.0)
        """
        face_embedding = self.engine.detect_face(frame)
        
        if face_embedding is None:
            return None, None, 0.0
        
        best_match_id = None
        best_match_name = None
        best_similarity = 0.0
        
        for teacher_id, data in self.teacher_data.items():
            for stored_embedding in data["embeddings"]:
                similarity = self.engine.calculate_similarity(face_embedding, stored_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_id = teacher_id
                    best_match_name = data["name"]
        
        if best_similarity >= self.threshold:
            self.update_last_login(best_match_id)
            return best_match_id, best_match_name, best_similarity
        else:
            return None, None, best_similarity
    
    def update_last_login(self, teacher_id):
        """Update teacher's last login time"""
        db = sessionLocal()
        teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
        if teacher:
            teacher.last_login = datetime.utcnow()
            db.commit()
        db.close()