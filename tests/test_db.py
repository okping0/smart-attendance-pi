from database.database import test_connection, create_all_tables

if __name__ == "__main__":
  print("Testing databse...")
  if test_connection():
    create_all_tables()
    print("\n Database setup complete!")
  else:
    print("\n Fix Database connection first")