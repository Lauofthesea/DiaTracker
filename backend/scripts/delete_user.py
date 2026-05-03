"""Script to delete a user account."""
import sys
sys.path.insert(0, '.')

from app.db.database import SessionLocal
from app.models.user import User

def delete_user(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.delete(user)
            db.commit()
            print(f"✓ User {email} deleted successfully")
        else:
            print(f"✗ User {email} not found")
    finally:
        db.close()

if __name__ == "__main__":
    delete_user("school.lauhipolito@gmail.com")
