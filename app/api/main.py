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


@app.patch("/session/end")
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

@app.post("/students/enroll")
def enroll_students(
  student_id: str,
  name: str,
  email: str = None,
  db: Session = Depends(get_db)
):
  
  from app.database.models import Student

# check if student alreeady exist
  existing = db.query(Student).filter(Student.student_id == student_id).first()
  if existing:
    return {"success": False, "message": "Student ID already exists"}
  
  student = Student(
    student_id=student_id,
    name=name,
    email=email,
    face_encodings=[]
  )

  db.add(student)
  db.commit()

  return {"success": True, "message": f"Student {name} enrolled", "student_id": student_id}



@app.post("/attendance/mark-manual")
def mark_manual_attendance(
  student_id: str,
  db: Session = Depends(get_db)
):
  
  from app.core.attendance_engine import AttendanceEngine
  from app.database.models import Student, Session as SessionModel

  active = db.query(SessionModel).filter(SessionModel.is_active == True).first()
  if not active:
    return {"success": False, "message": "No active session"}
  
  student = db.query(Student).filter(Student.student_id == student_id).first()
  if not student:
    return {"success": False, "message": "Student not found"}
  
  engine = AttendanceEngine(db)
  engine.current_session_id = active.id

  result = engine.mark_attendance(student_id, student.name, confidence=1.0)

  return result


@app.get("/session/history")
def get_session_history(limit: int = 10, db: Session = Depends(get_db)):
  from app.database.models import Session as SessionModel

  sessions = db.query(SessionModel).order_by(
    SessionModel.started_at.desc()
  ).limit(limit).all()

  return {
    "success": True,
    "sessions": [
      {
        "id": s.id,
        "session_name": s.session_name,
        "started_at": s.started_at.strftime("%Y-%m-%d %H:%M"),
        "ended_at": s.ended_at.strftime("%Y-%m-%d %H:%M") if s.ended_at else None,
        "is_active": s.is_active,
        "present_count": s.present_count,
        "total_students": s.total_students
      }
      for s in sessions
    ]
  }