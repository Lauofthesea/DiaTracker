"""
Reload database with enriched GI foods (with real USDA nutritional data).
"""

import sys
import csv
import logging
from pathlib import Path
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.database import SessionLocal
from app.models import Food, Nutrient, FoodNutrient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reload_enriched_foods():
    """Load enriched GI database with real USDA nutritional data."""
    
    db = SessionLocal()
    
    try:
        logger.info("=" * 80)
        logger.info("Reloading database with enriched GI foods")
        logger.info("=" * 80)
        
        # Path to enriched CSV
        csv_path = Path(__file__).parent.parent.parent / "datasets" / "gi_database_enriched.csv"
        
        if not csv_path.exists():
            logger.error(f"Enriched CSV not found at: {csv_path}")
            return
        
        logger.info(f"Loading from: {csv_path}")
        
        # Clear existing data
        logger.info("\nClearing existing food data...")
        db.execute(text("DELETE FROM food_nutrients"))
        db.execute(text("DELETE FROM food_entries"))
        db.execute(text("DELETE FROM foods"))
        db.execute(text("DELETE FROM nutrients"))
        db.commit()
        logger.info("✓ Cleared existing data")
        
        # Read CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            foods_data = list(reader)
        
        logger.info(f"\n✓ Found {len(foods_data)} foods in enriched CSV")
        
        # Create nutrients
        logger.info("\nCreating nutrient definitions...")
        carbs_nutrient = Nutrient(name="Carbohydrate", unit="g", nutrient_type="macronutrient")
        energy_nutrient = Nutrient(name="Energy", unit="kcal", nutrient_type="energy")
        fiber_nutrient = Nutrient(name="Fiber", unit="g", nutrient_type="macronutrient")
        protein_nutrient = Nutrient(name="Protein", unit="g", nutrient_type="macronutrient")
        fat_nutrient = Nutrient(name="Fat", unit="g", nutrient_type="macronutrient")
        
        db.add_all([carbs_nutrient, energy_nutrient, fiber_nutrient, protein_nutrient, fat_nutrient])
        db.flush()
        logger.info("✓ Created 5 nutrient definitions")
        
        # Load foods
        logger.info("\nLoading foods with USDA nutritional data...")
        inserted_count = 0
        skipped_count = 0
        
        for row in foods_data:
            food_name = row['food_name']
            category = row['food_category']
            
            # Skip reference foods
            if category == "Reference":
                skipped_count += 1
                continue
            
            # Get nutritional values from enriched CSV (per 100g from USDA)
            gi_value = float(row['gi_value'])
            gl_value = float(row['gl_value'])
            serving_size = float(row['serving_size_g'])
            available_carbs = float(row['available_carbs_g'])
            
            # Get real nutritional data from USDA (already per 100g)
            calories_per_100g = float(row['calories_per_100g'])
            protein_per_100g = float(row['protein_per_100g'])
            fat_per_100g = float(row['fat_per_100g'])
            fiber_per_100g = float(row['fiber_per_100g'])
            carbs_per_100g = float(row['carbohydrates_per_100g'])
            
            # Use available_carbs from GI database if USDA carbs is 0 or very different
            if carbs_per_100g == 0 or abs(carbs_per_100g - (available_carbs / serving_size * 100)) > 20:
                carbs_per_100g = (available_carbs / serving_size) * 100
            
            # Build description with GI/GL and data source
            usda_source = row.get('usda_food_name', '')
            match_score = row.get('match_score', '')
            description = f"GI: {gi_value}, GL: {gl_value}, Serving: {serving_size}g"
            if usda_source:
                description += f" | USDA: {usda_source} (match: {match_score})"
            
            # Create food
            food = Food(
                name=food_name,
                description=description,
                category=category,
                food_type="natural"
            )
            db.add(food)
            db.flush()
            
            # Add nutrients with REAL values from USDA
            db.add(FoodNutrient(
                food_id=food.food_id,
                nutrient_id=carbs_nutrient.nutrient_id,
                amount=Decimal(str(round(carbs_per_100g, 2))),
                per_unit="100g"
            ))
            db.add(FoodNutrient(
                food_id=food.food_id,
                nutrient_id=energy_nutrient.nutrient_id,
                amount=Decimal(str(round(calories_per_100g, 2))),
                per_unit="100g"
            ))
            db.add(FoodNutrient(
                food_id=food.food_id,
                nutrient_id=fiber_nutrient.nutrient_id,
                amount=Decimal(str(round(fiber_per_100g, 2))),  # REAL USDA data
                per_unit="100g"
            ))
            db.add(FoodNutrient(
                food_id=food.food_id,
                nutrient_id=protein_nutrient.nutrient_id,
                amount=Decimal(str(round(protein_per_100g, 2))),  # REAL USDA data
                per_unit="100g"
            ))
            db.add(FoodNutrient(
                food_id=food.food_id,
                nutrient_id=fat_nutrient.nutrient_id,
                amount=Decimal(str(round(fat_per_100g, 2))),  # REAL USDA data
                per_unit="100g"
            ))
            
            inserted_count += 1
            
            if inserted_count % 50 == 0:
                logger.info(f"  Loaded {inserted_count} foods...")
        
        db.commit()
        
        logger.info("\n" + "=" * 80)
        logger.info("SUCCESS!")
        logger.info("=" * 80)
        logger.info(f"✓ Loaded {inserted_count} foods with real USDA nutritional data")
        logger.info(f"✓ Skipped {skipped_count} reference foods")
        logger.info(f"\nData sources:")
        logger.info(f"  - GI/GL values: Foster-Powell 2002, Atkinson 2021")
        logger.info(f"  - Nutritional data: USDA FoodData Central")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"\n✗ Error loading enriched foods: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    reload_enriched_foods()
