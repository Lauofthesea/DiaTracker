"""
Script to populate food database from food_lookup_database.csv

This script reads the food lookup CSV and populates the database with
common foods and their nutritional information.
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


def populate_from_lookup_csv(csv_path: str, limit: int = 100):
    """
    Populate database from food_lookup_database.csv
    
    Args:
        csv_path: Path to the CSV file
        limit: Maximum number of foods to import (default 100)
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
        
        # Read CSV file
        foods_added = 0
        nutrients_added = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if foods_added >= limit:
                    break
                
                try:
                    food_name = row['food_name']
                    
                    # Skip if food already exists
                    existing = db.query(Food).filter(Food.name == food_name).first()
                    if existing:
                        logger.debug(f"Skipping existing food: {food_name}")
                        continue
                    
                    # Determine category
                    category = "Branded Foods"
                    if row.get('food_category'):
                        category = row['food_category']
                    
                    # Create food entry
                    food = Food(
                        name=food_name,
                        description=f"FDC ID: {row['fdc_id']}",
                        category=category,
                        food_type=row.get('data_type', 'branded_food'),
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
                            
                            # Special handling for sodium (convert mg to mg, already in mg)
                            # All other nutrients are per 100g
                            
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
        
        logger.info(f"Successfully added {foods_added} foods with {nutrients_added} nutrient entries")
        
    except Exception as e:
        logger.error(f"Error populating database: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main entry point for the script."""
    logger.info("Food Database Population from Lookup CSV")
    logger.info("=" * 50)
    
    # Get CSV path from command line or use default
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "../datasets/food_lookup_database.csv"
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        logger.error("Please provide the path to food_lookup_database.csv")
        sys.exit(1)
    
    logger.info(f"CSV file: {csv_path.absolute()}")
    
    # Get limit from command line or use default
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    logger.info(f"Import limit: {limit} foods")
    
    try:
        populate_from_lookup_csv(str(csv_path), limit)
        logger.info("=" * 50)
        logger.info("Database population completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
