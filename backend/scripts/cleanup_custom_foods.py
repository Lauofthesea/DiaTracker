"""
Script to clean up custom food entries that were created without nutrients.

This script deletes custom foods and their associated food entries.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.db.database import SessionLocal
from app.models import Food, FoodEntry, FoodNutrient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cleanup_custom_foods():
    """Clean up custom food entries."""
    db = SessionLocal()
    
    try:
        # Get all custom foods
        custom_foods = db.query(Food).filter(Food.food_type == 'custom').all()
        
        if not custom_foods:
            logger.info("No custom foods found to clean up.")
            return
        
        logger.info(f"Found {len(custom_foods)} custom foods to clean up")
        
        deleted_entries = 0
        deleted_nutrients = 0
        deleted_foods = 0
        
        for food in custom_foods:
            logger.info(f"Processing: {food.name} (ID: {food.food_id})")
            
            # Delete associated food entries
            entries = db.query(FoodEntry).filter(FoodEntry.food_id == food.food_id).all()
            for entry in entries:
                db.delete(entry)
                deleted_entries += 1
            
            # Delete associated food nutrients
            nutrients = db.query(FoodNutrient).filter(FoodNutrient.food_id == food.food_id).all()
            for nutrient in nutrients:
                db.delete(nutrient)
                deleted_nutrients += 1
            
            # Delete the food itself
            db.delete(food)
            deleted_foods += 1
        
        db.commit()
        
        logger.info(f"Cleanup complete:")
        logger.info(f"  - Deleted {deleted_foods} custom foods")
        logger.info(f"  - Deleted {deleted_entries} food entries")
        logger.info(f"  - Deleted {deleted_nutrients} food nutrients")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main entry point for the script."""
    logger.info("Custom Foods Cleanup Script")
    logger.info("=" * 50)
    
    try:
        cleanup_custom_foods()
        logger.info("=" * 50)
        logger.info("Cleanup completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
