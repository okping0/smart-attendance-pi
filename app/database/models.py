from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Student(Base):
  __tablename__ = "students"

  id = Column(Integer, primary_key=True, nullable=False, index=True)
  student_id = Column(String(20), unique=True, nullable=False, index=True)
  name = Column(String(100), nullable=False)
  email = Column(String(100), unique=True)
  face_embeddings = Column(JSON, nullable=False)

  attendance_records = relationship("AttendanceRecord", back_populates="student")

class Session(Base):
  __tablename__ = "sessions"

  id = Column(Integer, primary_key=True, index=True)
  Session_name = Column(String(100), nullable=False)
  class_name = Column(String(50))
  started_at = Column(DateTime, default=datetime.utcnow)
  ended_at = Column(DateTime, nullable=True)
  total_students = Column(Integer, default=80)
  present_count = Column(Integer, default=0)

  attendace_records = relationship("AttendanceRecords", back_populates="session")

class AttendanceRecord(Base):
  __tablename__ = "attendance_records"

  id = Column(Integer, primary_key=True, index=True)
  student_id = Column(Integer, ForeignKey("students.id"),nullable=False)
  session_id = Column(Integer, ForeignKey("sessions.id"), nullable= False)
  marked_at = Column(DateTime, default = datetime.utcnow)
  confidence_score = Column(Float)
  blink_detected = Column(Boolean, default=False)
  retry_count = Column(Integer, default=0)
  status = Column(String(20), default="absent")
  notes = Column(Text, nullable=True)

  student = relationship("Student", back_populates="attendace_records")
  session = relationship("Session", back_populates="attendance_records")

class SystemLog(Base):
  __tablename__ = "system_logs"

  id=Column(Integer, primary_key=True, index=True)
  timestamp = Column(DateTime, default=datetime.utcnow, index=True)
  level = Column (String(20))
  component = Column(String(20))
  message = Column(Text)
  student_id = Column(String(20), nullable=True)
  session_id = Column(Integer, nullable=True)
  session_id = Column(Integer, nullable=True)
  extra_data = Column(JSON, nullable=True)

