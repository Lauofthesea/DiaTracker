"""
Script to populate database with Filipino foods.

This script clears existing foods and populates with Filipino foods data.
"""

import sys
import csv
import logging
from pathlib import Path
from decimal import Decimal

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.db.database import SessionLocal
from app.models import Food, Nutrient, FoodNutrient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clear_existing_foods(db):
    """Clear all existing foods from database."""
    try:
        # First delete all food entries
        from app.models import FoodEntry
        entry_count = db.query(FoodEntry).delete()
        logger.info(f"Cleared {entry_count} food entries")
        
        # Then delete all foods (will cascade to food_nutrients)
        food_count = db.query(Food).delete()
        db.commit()
        logger.info(f"Cleared {food_count} existing foods")
    except Exception as e:
        logger.error(f"Error clearing foods: {e}")
        db.rollback()
        raise


def populate_filipino_foods(csv_path: str):
    """
    Populate database with Filipino foods from CSV.
    
    Args:
        csv_path: Path to the Filipino foods CSV file
    """
    db = SessionLocal()
    
    try:
        # Get nutrient IDs
        nutrients = {}
        for nutrient in db.query(Nutrient).all():
            nutrients[nutrient.name] = nutrient.nutrient_id
        
        logger.info(f"Found {len(nutrients)} nutrients in database")
        
        # Check if we have the required nutrients
        required_nutrients = {
            'Energy': 'calories',
            'Carbohydrate, by difference': 'carbs_total',
            'Protein': 'protein',
            'Total lipid (fat)': 'fat_total',
            'Fiber, total dietary': 'fiber',
            'Sugars, total including NLEA': 'sugars_total',
            'Sodium, Na': 'sodium'
        }
        
        missing_nutrients = []
        for nutrient_name in required_nutrients.keys():
            if nutrient_name not in nutrients:
                missing_nutrients.append(nutrient_name)
        
        if missing_nutrients:
            logger.error(f"Missing required nutrients: {missing_nutrients}")
            logger.error("Please run: python scripts/seed_nutrients.py")
            return
        
        # Clear existing foods
        logger.info("Clearing existing foods...")
        clear_existing_foods(db)
        
        # Read CSV file
        foods_added = 0
        nutrients_added = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    food_name = row['food_name']
                    category = row.get('category', 'Filipino Food')
                    
                    # Create food entry
                    food = Food(
                        name=food_name,
                        description=f"Filipino cuisine - {category}",
                        category=category,
                        food_type='filipino',
                        allergens=None
                    )
                    
                    db.add(food)
                    db.flush()  # Get the food_id
                    
                    # Add nutritional data
                    for nutrient_name, csv_column in required_nutrients.items():
                        value = row.get(csv_column, '0')
                        if not value or value == '':
                            value = '0'
                        
                        try:
                            amount = Decimal(value)
                            
                            # Skip if amount is 0
                            if amount == 0:
                                continue
                            
                            food_nutrient = FoodNutrient(
                                food_id=food.food_id,
                                nutrient_id=nutrients[nutrient_name],
                                amount=amount,
                                per_unit="100g"
                            )
                            
                            db.add(food_nutrient)
                            nutrients_added += 1
                            
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Invalid value for {nutrient_name} in {food_name}: {value}")
                            continue
                    
                    foods_added += 1
                    
                    if foods_added % 10 == 0:
                        logger.info(f"Added {foods_added} foods...")
                        db.commit()
                
                except Exception as e:
                    logger.error(f"Error processing row: {e}")
                    logger.error(f"Row data: {row}")
                    db.rollback()
                    continue
        
        db.commit()
        
        logger.info(f"Successfully added {foods_added} Filipino foods with {nutrients_added} nutrient entries")
        
    except Exception as e:
        logger.error(f"Error populating database: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main entry point for the script."""
    logger.info("Filipino Foods Database Population")
    logger.info("=" * 50)
    
    # Get CSV path from command line or use default
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "../datasets/filipino_foods.csv"
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        logger.error("Please ensure filipino_foods.csv exists in datasets folder")
        sys.exit(1)
    
    logger.info(f"CSV file: {csv_path.absolute()}")
    
    # Confirm before clearing
    logger.warning("This will DELETE all existing foods and replace with Filipino foods!")
    response = input("Continue? (yes/no): ")
    
    if response.lower() != 'yes':
        logger.info("Operation cancelled")
        sys.exit(0)
    
    try:
        populate_filipino_foods(str(csv_path))
        logger.info("=" * 50)
        logger.info("Filipino foods database population completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
