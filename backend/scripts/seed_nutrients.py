"""
Script to seed the nutrients table with basic nutrients.

This script creates the essential nutrients needed for custom food entries.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.db.database import SessionLocal
from app.models import Nutrient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def seed_nutrients():
    """Seed the nutrients table with basic nutrients."""
    db = SessionLocal()
    
    try:
        # Check if nutrients already exist
        existing_count = db.query(Nutrient).count()
        if existing_count > 0:
            logger.info(f"Nutrients table already has {existing_count} entries. Skipping seed.")
            return
        
        # Define basic nutrients
        nutrients = [
            {
                "name": "Energy",
                "unit": "KCAL",
                "nutrient_type": "macronutrient"
            },
            {
                "name": "Carbohydrate, by difference",
                "unit": "G",
                "nutrient_type": "macronutrient"
            },
            {
                "name": "Protein",
                "unit": "G",
                "nutrient_type": "macronutrient"
            },
            {
                "name": "Total lipid (fat)",
                "unit": "G",
                "nutrient_type": "macronutrient"
            },
            {
                "name": "Fiber, total dietary",
                "unit": "G",
                "nutrient_type": "macronutrient"
            },
            {
                "name": "Sugars, total including NLEA",
                "unit": "G",
                "nutrient_type": "macronutrient"
            },
            {
                "name": "Sodium, Na",
                "unit": "MG",
                "nutrient_type": "mineral"
            },
            {
                "name": "Cholesterol",
                "unit": "MG",
                "nutrient_type": "other"
            }
        ]
        
        # Insert nutrients
        inserted_count = 0
        for nutrient_data in nutrients:
            nutrient = Nutrient(**nutrient_data)
            db.add(nutrient)
            inserted_count += 1
            logger.info(f"Added nutrient: {nutrient_data['name']}")
        
        db.commit()
        logger.info(f"Successfully seeded {inserted_count} nutrients")
        
    except Exception as e:
        logger.error(f"Error seeding nutrients: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main entry point for the script."""
    logger.info("Nutrient Seeding Script")
    logger.info("=" * 50)
    
    try:
        seed_nutrients()
        logger.info("=" * 50)
        logger.info("Nutrient seeding completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
