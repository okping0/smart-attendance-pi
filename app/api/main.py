from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session
from app.database.database import get_db

app = FastAPI(title="Attendance System API")

@app.get("/")
def root():
  return {"message": "Attendance system API"}

@app.post("/session/start")
def start_session(
  session_name: str,
  class_name: str,
  total_students : int = 80,
  db: Session = Depends(get_db)
):
  from app.core.attendance_engine import AttendanceEngine

  engine = AttendanceEngine(db)
  session_id = engine.start_session(session_name, total_students=total_students,class_name=class_name)

  return {"success": True, "session_id": session_id}

@app.get("/session/status")
def get_session_status(db: Session = Depends(get_db)):
  from app.core.attendance_engine import AttendanceEngine
  from app.database.models import Session as SessionModel

  active = db.query(SessionModel).filter(SessionModel.is_active == True).first()

  if not active:
    return {"active": False}
  
  return{
    "active": True,
    "session_id": active.id,
    "session_name": active.session_name,
    "present_count": active.present_count,
    "total_students": active.total_students
  }


@app.post("/session/end")
def end_sesion(db: Session = Depends(get_db)):
  from app.core.attendance_engine import AttendanceEngine

  engine = AttendanceEngine(db)

  from app.database.models import Session as SessionModel
  from datetime import datetime

  active = db.query(SessionModel).filter(SessionModel.is_active == True).first()

  if not active:
    return{"success": False, "message": "no active session"}
  
  active.is_active = False
  active.ended_at = datetime.utcnow()
  db.commit()

  stats = {
    "session_name": active.session_name,
    "present": active.present_count,
    "total": active.total_students,
    "rate": round(active.present_count / active.total_students *100, 1) if active.total_students > 0 else 0
  }

  return {"success": True, "stats": stats}

@app.get("/attendance/list")
def get_attendance_list(session_id: int = None, db: Session = Depends(get_db)):
  from app.database.models import AttendanceRecord, Student, Session as SessionModel

# if there is no session id given, get active session 
  if not session_id:
    active = db.query(SessionModel).filter(SessionModel.is_active == True).first()

    if not active:
      return {"success": False, "message": "No active session"}
    session_id = active.id

# getting attendance records
  records = db.query(AttendanceRecord, Student).join(
    Student, AttendanceRecord.student_id == Student.id
  ).filter(
    AttendanceRecord.session_id == session_id
  ).all()

  attendance_list = [
    {
      "student_id": student.student_id,
      "student_name": student.name,
      "marked_at": record.marked_at.strftime("%H:%M:%S"),
      "confidence": record.confidence_score
    }
    for record, student in records
  ]

  return{
    "success": True,
    "session_id": session_id,
    "count": len(attendance_list),
    "attendance": attendance_list
  }
  