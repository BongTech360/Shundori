"""
Database initialization and migration script.
Run this once to set up the database schema.
"""
from database import init_db, engine, Base
from sqlalchemy import inspect

def check_tables_exist():
    """Check if tables already exist."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    return len(existing_tables) > 0

def main():
    """Initialize database."""
    print("Initializing database...")
    
    if check_tables_exist():
        print("Tables already exist. Skipping creation.")
        response = input("Do you want to recreate all tables? (yes/no): ")
        if response.lower() == 'yes':
            Base.metadata.drop_all(bind=engine)
            print("Dropped existing tables.")
        else:
            print("Exiting without changes.")
            return
    
    init_db()
    print("Database initialized successfully!")
    print("\nTables created:")
    print("  - users")
    print("  - attendance_records")
    print("  - fines")
    print("  - settings")

if __name__ == '__main__':
    main()

