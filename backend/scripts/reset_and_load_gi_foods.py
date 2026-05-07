"""
Script to clear old food data and load foods from the GI database CSV.
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
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clear_food_data(db):
    """Clear all existing food data"""
    logger.info("Clearing existing food data...")
    
    try:
        # Delete in correct order due to foreign keys
        db.execute(text("DELETE FROM food_nutrients"))
        db.execute(text("DELETE FROM food_entries"))
        db.execute(text("DELETE FROM foods"))
        db.execute(text("DELETE FROM nutrients"))
        db.commit()
        logger.info("✓ Cleared all food data")
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        db.rollback()
        raise


def load_gi_database(db):
    """Load foods from gi_database_research_only.csv"""
    
    # Path to GI database CSV
    csv_path = Path(__file__).parent.parent.parent / "datasets" / "gi_database_research_only.csv"
    
    if not csv_path.exists():
        logger.error(f"GI database CSV not found at: {csv_path}")
        return 0
    
    logger.info(f"Loading GI database from: {csv_path}")
    
    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        foods_data = list(reader)
    
    logger.info(f"Found {len(foods_data)} foods in CSV")
    
    # Create nutrients first
    logger.info("Creating nutrients...")
    
    carbs_nutrient = Nutrient(
        name="Carbohydrate",
        unit="g",
        nutrient_type="macronutrient"
    )
    db.add(carbs_nutrient)
    
    energy_nutrient = Nutrient(
        name="Energy",
        unit="kcal",
        nutrient_type="energy"
    )
    db.add(energy_nutrient)
    
    fiber_nutrient = Nutrient(
        name="Fiber",
        unit="g",
        nutrient_type="macronutrient"
    )
    db.add(fiber_nutrient)
    
    protein_nutrient = Nutrient(
        name="Protein",
        unit="g",
        nutrient_type="macronutrient"
    )
    db.add(protein_nutrient)
    
    fat_nutrient = Nutrient(
        name="Fat",
        unit="g",
        nutrient_type="macronutrient"
    )
    db.add(fat_nutrient)
    
    db.flush()
    logger.info("✓ Created 5 nutrients")
    
    inserted_count = 0
    skipped_count = 0
    
    for row in foods_data:
        try:
            food_name = row['food_name']
            category = row['food_category']
            
            # Skip reference foods
            if category == "Reference":
                skipped_count += 1
                continue
            
            # Get nutritional values
            gi_value = float(row['gi_value'])
            gl_value = float(row['gl_value'])
            serving_size = float(row['serving_size_g'])
            available_carbs = float(row['available_carbs_g'])
            
            # Estimate calories (4 kcal per g carbs - simplified)
            # Scale to per 100g
            carbs_per_100g = (available_carbs / serving_size) * 100
            calories_per_100g = carbs_per_100g * 4
            
            # Create food
            food = Food(
                name=food_name,
                description=f"GI: {gi_value}, GL: {gl_value}, Serving: {serving_size}g",
                category=category,
                food_type="natural"
            )
            
            db.add(food)
            db.flush()
            
            # Add carbohydrate nutrient (per 100g)
            food_nutrient_carbs = FoodNutrient(
                food_id=food.food_id,
                nutrient_id=carbs_nutrient.nutrient_id,
                amount=Decimal(str(round(carbs_per_100g, 2))),
                per_unit="100g"
            )
            db.add(food_nutrient_carbs)
            
            # Add energy nutrient (per 100g)
            food_nutrient_energy = FoodNutrient(
                food_id=food.food_id,
                nutrient_id=energy_nutrient.nutrient_id,
                amount=Decimal(str(round(calories_per_100g, 2))),
                per_unit="100g"
            )
            db.add(food_nutrient_energy)
            
            # Add default fiber (2g per 100g - rough estimate)
            food_nutrient_fiber = FoodNutrient(
                food_id=food.food_id,
                nutrient_id=fiber_nutrient.nutrient_id,
                amount=Decimal("2.0"),
                per_unit="100g"
            )
            db.add(food_nutrient_fiber)
            
            # Add default protein (5g per 100g - rough estimate)
            food_nutrient_protein = FoodNutrient(
                food_id=food.food_id,
                nutrient_id=protein_nutrient.nutrient_id,
                amount=Decimal("5.0"),
                per_unit="100g"
            )
            db.add(food_nutrient_protein)
            
            # Add default fat (3g per 100g - rough estimate)
            food_nutrient_fat = FoodNutrient(
                food_id=food.food_id,
                nutrient_id=fat_nutrient.nutrient_id,
                amount=Decimal("3.0"),
                per_unit="100g"
            )
            db.add(food_nutrient_fat)
            
            inserted_count += 1
            
            if inserted_count % 50 == 0:
                logger.info(f"Inserted {inserted_count} foods...")
                db.commit()
        
        except Exception as e:
            logger.error(f"Error inserting {row.get('food_name', 'unknown')}: {e}")
            db.rollback()
            raise
    
    db.commit()
    logger.info(f"✓ Inserted {inserted_count} foods (skipped {skipped_count} reference foods)")
    
    return inserted_count


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("GI Database Food Loader")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Step 1: Clear old data
        clear_food_data(db)
        
        # Step 2: Load GI database
        count = load_gi_database(db)
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✓ Successfully loaded {count} foods from GI database")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        db.rollback()
        return 1
    
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
