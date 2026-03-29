import numpy as np
from insightface.app import FaceAnalysis
from typing import Optional, Tuple 
import pickle
import os

class FaceRecognitionEngine:
  def __init__(self, model_name: str = "buffalo_sc"):
    self.model_name = model_name
    self.app = None
    self.student_embeddings = {}
    self.threshold = 0.40

  def load_model(self):
    print("Loading face recognition model...")
    self.app = FaceAnalysis(name=self.model_name, providers = ['CPUExecutionProvider'])
    self.app.prepare(ctx_id = 1, det_size=(640, 480))
    print("Model loaded")

  def detect_face(self, image: np.ndarray) -> Optional[np.ndarray]:
    if self.app is None:
      raise RuntimeError("Model not loaded yet!")
    
    faces = self.app.get(image)
    if len(faces) == 0:
      return None
    
    if len(faces) >1:
      faces = sorted(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse = True)

    return faces[0].embedding
  
  def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    similarity = np.dot(embedding1, embedding2) / (
      np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
    )
    return float(similarity)
  
  def load_student_embeddings(self, embeddings_file: str = "data/embeddings.pkl"):
    if not os.path.exists(embeddings_file):
      print(f"No embeddings file found")
      return
    
    with open(embeddings_file, 'rb') as f:
      raw_data = pickle.load(f)

      self.student_embeddings = {}
    for student_id, info in raw_data.items():
      self.student_embeddings[student_id] = {
          "name": info["name"],
          "embeddings": info["embeddings"]
      }

    print(f"Load {len(self.student_embeddings)} students")

  def recognize_face(self, image: np.ndarray) -> Tuple[Optional[str], float]:
    face_embedding = self.detect_face(image)

    if face_embedding is None:
      return None, 0.0
    
    best_match_id = None
    best_match_name = None
    best_similarity = 0.0

    for student_id, info in self.student_embeddings.items():
      for stored_embedding in info["embeddings"]:
        similarity = self.calculate_similarity(face_embedding, stored_embedding)
                
        if similarity > best_similarity:
          best_similarity = similarity
          best_match_id = student_id
          best_match_name = info["name"]
        
    if best_similarity >= self.threshold:
      return best_match_id, best_match_name,best_similarity
    else:
      return None,None, best_similarity
    
  def generate_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        return self.detect_face(image)