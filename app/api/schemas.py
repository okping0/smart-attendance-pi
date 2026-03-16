from pydantic import BaseModel
from typing import Optional

class SessionStartRequest(BaseModel):
    session_name: str
    class_name: str
    total_students: int = 80

class StudentEnrollRequest(BaseModel):
    student_id: str
    name: str
    email: Optional[str] = None

class ManualAttendanceRequest(BaseModel):
    student_id: str