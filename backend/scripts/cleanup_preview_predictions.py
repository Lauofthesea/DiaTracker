"""
Clean up preview predictions (predictions without food_entry_id).

This script removes meal predictions that were created during preview
(when user was adding items but didn't confirm the meal).
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from app.core.config import settings


def cleanup_preview_predictions():
    """Delete all meal predictions that don't have a food_entry_id."""
    
    engine = create_engine(str(settings.DATABASE_URL))
    
    with engine.connect() as conn:
        # Check how many preview predictions exist
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM meal_predictions
            WHERE food_entry_id IS NULL;
        """))
        count = result.fetchone()[0]
        
        if count == 0:
            print("✅ No preview predictions found. Database is clean!")
            return
        
        print(f"Found {count} preview prediction(s) to delete...")
        
        # Delete preview predictions
        conn.execute(text("""
            DELETE FROM meal_predictions
            WHERE food_entry_id IS NULL;
        """))
        
        conn.commit()
        
        print(f"✅ Deleted {count} preview prediction(s)!")
        
        # Show remaining predictions
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM meal_predictions
            WHERE food_entry_id IS NOT NULL;
        """))
        remaining = result.fetchone()[0]
        
        print(f"✅ {remaining} confirmed meal prediction(s) remaining in database.")


if __name__ == "__main__":
    print("=" * 60)
    print("Cleaning up preview predictions...")
    print("=" * 60)
    
    try:
        cleanup_preview_predictions()
        print("\n✅ Cleanup complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
