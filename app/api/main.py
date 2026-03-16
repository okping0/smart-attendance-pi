from fastapi import FastAPI,Depends
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.schemas import SessionStartRequest, StudentEnrollRequest, ManualAttendanceRequest
import csv, io, os

app = FastAPI(title="Attendance System API")

static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/dashboard")
def dashboard():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(html_path)

@app.get("/")
def root():
  return {"message": "Attendance system API"}



# ------- start session ------- #
# ----------------------------- #


@app.post("/session/start")
def start_session(
  data: SessionStartRequest,
  db: Session = Depends(get_db)
):
  from app.core.attendance_engine import AttendanceEngine

  engine = AttendanceEngine(db)
  session_id = engine.start_session(data.session_name, total_students=data.total_students,class_name=data.class_name)

  return {"success": True, "session_id": session_id}

# ---------------------------------------------------#




# ------- session status ------- #
# ----------------------------- #
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

# ---------------------------------------------------#




# ------- end session ------- #
# ----------------------------- #
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

# ---------------------------------------------------#




# ------- get attendance list ------- #
# ----------------------------- #
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

# ---------------------------------------------------#




# ------- enroll students ------- #
# ----------------------------- #
@app.post("/students/enroll")
def enroll_students(
  data: StudentEnrollRequest,
  db: Session = Depends(get_db)
):
  
  from app.database.models import Student

# check if student alreeady exist
  existing = db.query(Student).filter(Student.student_id == data.student_id).first()
  if existing:
    return {"success": False, "message": "Student ID already exists"}
  
  student = Student(
    student_id=data.student_id,
    name=data.name,
    email=data.email,
    face_encodings=[]
  )

  db.add(student)
  db.commit()

  return {"success": True, "message": f"Student {data.name} enrolled", "student_id": data.student_id}

# ---------------------------------------------------#




# ------- mark manual attendance ------- #
# ----------------------------- #
@app.post("/attendance/mark-manual")
def mark_manual_attendance(
  data: ManualAttendanceRequest,
  db: Session = Depends(get_db)
):
  
  from app.core.attendance_engine import AttendanceEngine
  from app.database.models import Student, Session as SessionModel

  active = db.query(SessionModel).filter(SessionModel.is_active == True).first()
  if not active:
    return {"success": False, "message": "No active session"}
  
  student = db.query(Student).filter(Student.student_id == data.student_id).first()
  if not student:
    return {"success": False, "message": "Student not found"}
  
  engine = AttendanceEngine(db)
  engine.current_session_id = active.id

  result = engine.mark_attendance(data.student_id, student.name, confidence=1.0)

  return result

# ---------------------------------------------------#




# ------- session history ------- #
# ----------------------------- #
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

# ---------------------------------------------------#




# ------- session restart ------- #
# ----------------------------- #
@app.patch("/session/reopen")
def reopen_session(session_id: int, db: Session = Depends(get_db)):
  from app.database.models import Session as SessionModel

  session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

  if not session:
    return {"success": False, "message": "Session not found"}
    
  if session.is_active:
    return {"success": False, "message": "Session is already active"}
    
  # Close any other active sessions first
  active_sessions = db.query(SessionModel).filter(SessionModel.is_active == True).all()
  for s in active_sessions:
    s.is_active = False
    
  # Reopen this session
  session.is_active = True
  session.ended_at = None
    
  db.commit()
    
  return {
    "success": True,
    "message": f"Session '{session.session_name}' reopened",
    "session_id": session.id
    }

# ---------------------------------------------------#



@app.get("/attendance/export")
def export_attendance(session_id: int, db: Session = Depends(get_db)):
  from app.database.models import AttendanceRecord,Student ,Session as SessionModel

  session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

  if not session:
    return {"success": False, "message": "Session not found"}
  
  # get records
  records = db.query(AttendanceRecord, Student).join(
    Student, AttendanceRecord.student_id == Student.id
  ).filter(
    AttendanceRecord.session_id == session_id
  ).all()

  output = io.StringIO()
  writer = csv.writer(output)

  writer.writerow(['Student ID', 'Name', 'Confidence', 'Status'])

  for record, student in records:
    writer.writerow([
      student.student_id,
      student.name,
      record.marked_at.strftime("%Y-%m-%d %H:%M:%S"),
      f"{record.confidence_score:.2%}",
      record.status
    ])

  output.seek(0)

  filename = f"attendance_{session.session_name.replace(' ','_')}_{session_id}.csv"

  return StreamingResponse(
    iter([output.getvalue()]),
    media_type="text/csv",
    headers={"Content-Disposition": f"attachment; filename={filename}"}
  )