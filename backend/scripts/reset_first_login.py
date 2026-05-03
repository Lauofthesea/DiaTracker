"""
Reset a user's first login status to trigger the onboarding flow again.
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User


def reset_first_login(email: str):
    """Reset first_login_completed flag for a user."""
    db: Session = SessionLocal()
    try:
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User with email '{email}' not found.")
            return False
        
        # Reset first login flag
        user.first_login_completed = False
        db.commit()
        
        print(f"✅ Successfully reset first login for user: {user.name} ({user.email})")
        print(f"   User will see onboarding flow on next login.")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting first login: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reset_first_login.py <email>")
        print("Example: python reset_first_login.py john@test.com")
        sys.exit(1)
    
    email = sys.argv[1]
    reset_first_login(email)
