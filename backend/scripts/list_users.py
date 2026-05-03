"""Script to list all users."""
import sys
sys.path.insert(0, '.')

from app.db.database import SessionLocal
from app.models.user import User

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if users:
            print("Users in database:")
            for user in users:
                print(f"  - {user.email}")
        else:
            print("No users found")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
