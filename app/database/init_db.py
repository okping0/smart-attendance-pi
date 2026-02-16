import sys
import os

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root)

from app.database.database import test_connection, create_all_tables

if __name__ == "__main__":
  print("Testing database connection...")
  if test_connection():
    create_all_tables()
    print("\n Database ready")
  else:
    print("\n Fix databse connection first")