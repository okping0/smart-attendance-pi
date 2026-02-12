from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
  DB_USER = os.getenv("DB_USER", "postgres")
  DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
  DB_HOST = os.getenv("DB_HOST", "localhost")
  DB_PORT = os.getenv("DB_PORT", "5432")
  DB_NAME = os.getenv("DB_NAME", "attendance_db")

  return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(get_database_url(), echo = True, pool_pre_ping=True)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
  db = sessionLocal()
  try: 
    yield db
  finally:
    db.close()

def create_all_tables():
  from database.models import Base
  print("Creating database tables...")
  Base.metadata.create_all(bind=engine)
  print("All tables created")

def test_connection():
  try:
    db = sessionLocal()
    db.execute(text("SELECT 1"))
    db.close()
    print("Database connection successfull")
    return True
  except Exception as e:
    print(f"Database connection failed: {e}")
    return False