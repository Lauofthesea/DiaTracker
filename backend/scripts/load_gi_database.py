"""
Script to load foods from the GI database CSV into the database.
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
from sqlalchemy.exc import IntegrityError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_gi_database():
    """Load foods from gi_database_research_only.csv"""
    
    # Path to GI database CSV
    csv_path = Path(__file__).parent.parent.parent / "datasets" / "gi_database_research_only.csv"
    
    if not csv_path.exists():
        logger.error(f"GI database CSV not found at: {csv_path}")
        return
    
    logger.info(f"Loading GI database from: {csv_path}")
    
    db = SessionLocal()
    
    try:
        # Read CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            foods_data = list(reader)
        
        logger.info(f"Found {len(foods_data)} foods in CSV")
        
        # Get or create nutrients
        carbs_nutrient = db.query(Nutrient).filter(Nutrient.name == "Carbohydrate").first()
        if not carbs_nutrient:
            carbs_nutrient = Nutrient(
                name="Carbohydrate",
                unit="g",
                nutrient_type="macronutrient"
            )
            db.add(carbs_nutrient)
            db.flush()
        
        energy_nutrient = db.query(Nutrient).filter(Nutrient.name == "Energy").first()
        if not energy_nutrient:
            energy_nutrient = Nutrient(
                name="Energy",
                unit="kcal",
                nutrient_type="energy"
            )
            db.add(energy_nutrient)
            db.flush()
        
        inserted_count = 0
        duplicate_count = 0
        error_count = 0
        
        for row in foods_data:
            try:
                food_name = row['food_name']
                category = row['food_category']
                
                # Skip reference foods
                if category == "Reference":
                    continue
                
                # Check if food already exists
                existing = db.query(Food).filter(
                    Food.name == food_name,
                    Food.category == category
                ).first()
                
                if existing:
                    duplicate_count += 1
                    continue
                
                # Calculate calories from carbs (rough estimate: 4 kcal per g carbs)
                # This is a simplification - real foods have protein and fat too
                available_carbs = float(row['available_carbs_g'])
                estimated_calories = available_carbs * 4
                
                # Create food
                food = Food(
                    name=food_name,
                    description=f"GI: {row['gi_value']}, GL: {row['gl_value']}",
                    category=category,
                    food_type="natural"
                )
                
                db.add(food)
                db.flush()
                
                # Add carbohydrate nutrient
                food_nutrient_carbs = FoodNutrient(
                    food_id=food.food_id,
                    nutrient_id=carbs_nutrient.nutrient_id,
                    amount=Decimal(str(available_carbs)),
                    per_unit="100g"
                )
                db.add(food_nutrient_carbs)
                
                # Add energy nutrient
                food_nutrient_energy = FoodNutrient(
                    food_id=food.food_id,
                    nutrient_id=energy_nutrient.nutrient_id,
                    amount=Decimal(str(estimated_calories)),
                    per_unit="100g"
                )
                db.add(food_nutrient_energy)
                
                inserted_count += 1
                
                if inserted_count % 50 == 0:
                    logger.info(f"Inserted {inserted_count} foods...")
                    db.commit()
            
            except IntegrityError:
                db.rollback()
                duplicate_count += 1
                logger.warning(f"Duplicate food: {row['food_name']}")
            
            except Exception as e:
                db.rollback()
                error_count += 1
                logger.error(f"Error inserting {row['food_name']}: {e}")
        
        db.commit()
        
        logger.info("\n" + "=" * 50)
        logger.info("SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Foods inserted:     {inserted_count}")
        logger.info(f"Duplicates skipped: {duplicate_count}")
        logger.info(f"Errors:             {error_count}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("GI Database Loader")
    logger.info("=" * 50)
    load_gi_database()
    logger.info("Done!")
