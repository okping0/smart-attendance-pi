from datetime import datetime
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.database.models import Student, Session as SessionModel, AttendanceRecord, SystemLog


class AttendanceEngine:
  def __inti__(self, db: Session):
    self.db = db
    self.current_session_id = None

  def start_session(self, session_name: str, class_name: str, total_students: int = 80) -> int:
    active = self.db.query(SessionModel).filter(SessionModel.is_active == True).all()
    for s in active:
      s.is_active = False
      s.ended_at = datetime.utcnow()
    self.db.commit()

    new_session = SessionModel(
      session_name=session_name,
      total_students=total_students,
      started_at=datetime.utcnow(),
      is_active=True,
      present_count=0
    )

    self.db.add(new_session)
    self.db.commit()
    self.db.refresh(new_session)

    self.current_session_id=new_session.id
    print(f"Session started: {session_name} (ID: {new_session.id})")
    return new_session.id
  
  def mark_attendance(self, student_id: str, student_name:str, confidence:float) -> Dict:
    if not self.current_session_id:
      return{"success": False, "error": "NO_SESSION", "message":"No active session"}
    
    student = self.db.query(Student).filter(Student.student_id == student_id).first()

    if not student:
      return {"success": False, "error": "NOT_FOUND", "message": f"{student_id} not in database" }
    
    existing = self.db.query(AttendanceRecord).filter(
      AttendanceRecord.student_id == student.id,
      AttendanceRecord.session_id == self.current_session_id
    ).first()

    if existing:
      return {
        "success": False,
        "error": "DUPLICATE",
        "message": f"Already marked at {existing.marked_at.strftime('%I:%M %p')}"
      }
    
    #mark attendance
    record = AttendanceRecord(
      student_id=student.id,
      Session_id=self.current_session_id,
      marked_at=datetime.utcnow(),
      confidence_score=confidence,
      status="present"
    )
    self.db.add(record)

    session = self.db.query(SessionModel).filter(SessionModel.id == self.current_session_id).first()
    session.present_count += 1
    self.db.commit()

    return{
      "success": True,
      "student_id":student_id,
      "student_name":student_name,
      "marked_at": record.marked_at,
      "confidence":confidence,
      "present_count": session.present_count,
      "total": session.total_students
    }
    
  def get_status(self) -> Optional[Dict]:
    if not self.current_session_id:
      return None

    session = self.db.query(SessionModel).filter(SessionModel.id == self.current_session_id).first()
    if not session:
      return None

    return {
            "session_name": session.session_name,
            "present": session.present_count,
            "total": session.total_students
        }

  def end_session(self) -> Optional[Dict]:
    if not self.current_session_id:
      return None

    session = self.db.query(SessionModel).filter(SessionModel.id == self.current_session_id).first()
    session.is_active = False
    session.ended_at = datetime.utcnow()
    self.db.commit()

    stats = {
            "session_name": session.session_name,
            "present": session.present_count,
            "total": session.total_students,
            "rate": round(session.present_count / session.total_students * 100, 1)
    }

    self.current_session_id = None
    print(f"✅ Session ended - {stats['rate']}% attendance")
    return stats