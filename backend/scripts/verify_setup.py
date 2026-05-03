#!/usr/bin/env python3
"""
Verify backend setup script.
"""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def verify_imports():
    """Verify all imports work correctly."""
    try:
        print("Testing imports...")
        
        # Test core imports
        from app.core.config import settings
        print("✓ Core config imported")
        
        from app.core.security import get_password_hash, verify_password
        print("✓ Security utilities imported")
        
        # Test database imports
        from app.db.database import engine, get_db
        print("✓ Database connection imported")
        
        # Test model imports
        from app.models.user import User
        from app.models.health_metrics import HealthMetrics
        from app.models.food import Food
        print("✓ Database models imported")
        
        # Test FastAPI app
        from main import app
        print("✓ FastAPI app imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        return False


def verify_password_hashing():
    """Verify password hashing works."""
    try:
        print("\nTesting password hashing...")
        
        from app.core.security import get_password_hash, verify_password
        
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Verify the password
        is_valid = verify_password(password, hashed)
        
        if is_valid:
            print("✓ Password hashing and verification works")
            return True
        else:
            print("❌ Password verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Password hashing error: {e}")
        return False


def verify_config():
    """Verify configuration works."""
    try:
        print("\nTesting configuration...")
        
        from app.core.config import settings
        
        print(f"✓ Database URL configured: {settings.DATABASE_URL[:20]}...")
        print(f"✓ Secret key configured: {len(settings.SECRET_KEY)} characters")
        print(f"✓ API version: {settings.API_V1_STR}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def main():
    """Run all verification tests."""
    print("🔍 Verifying ML Diabetes Tracker Backend Setup\n")
    
    tests = [
        verify_imports,
        verify_config,
        verify_password_hashing,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 Backend setup verification complete! All systems operational.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())