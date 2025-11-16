"""
Database initialization and migration script for MongoDB.
Run this once to set up the database indexes.
"""
from database import init_db

def main():
    """Initialize database."""
    print("Initializing MongoDB database...")
    
    try:
        init_db()
        print("Database initialized successfully!")
        print("\nIndexes created for collections:")
        print("  - users (telegram_id, is_active)")
        print("  - attendance_records (user_id+date, date, user_id)")
        print("  - fines (user_id+date, date, user_id)")
        print("  - settings (key)")
        print("\nYou can now connect to MongoDB Compass using the connection string from your .env file.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == '__main__':
    main()
