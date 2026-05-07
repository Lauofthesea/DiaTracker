"""
Admin API endpoints for database management.
"""

import logging
import csv
from pathlib import Path
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.dependencies import get_db, get_current_user
from app.models import User, Food, Nutrient, FoodNutrient

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/load-gi-database")
def load_gi_database(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Load foods from the enriched GI database CSV.
    This will clear existing foods and load the 200 foods from gi_database_enriched.csv
    with real USDA nutritional data (protein, fat, fiber, calories).
    """
    try:
        logger.info("Starting enriched GI database load...")
        
        # Path to enriched GI database CSV
        csv_path = Path(__file__).parent.parent.parent.parent.parent / "datasets" / "gi_database_enriched.csv"
        
        if not csv_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"GI database CSV not found at: {csv_path}"
            )
        
        # Clear existing data
        logger.info("Clearing existing food data...")
        db.execute(text("DELETE FROM food_nutrients"))
        db.execute(text("DELETE FROM food_entries"))
        db.execute(text("DELETE FROM foods"))
        db.execute(text("DELETE FROM nutrients"))
        db.commit()
        
        # Read CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            foods_data = list(reader)
        
        logger.info(f"Found {len(foods_data)} foods in CSV")
        
        # Create nutrients
        carbs_nutrient = Nutrient(name="Carbohydrate", unit="g", nutrient_type="macronutrient")
        energy_nutrient = Nutrient(name="Energy", unit="kcal", nutrient_type="energy")
        fiber_nutrient = Nutrient(name="Fiber", unit="g", nutrient_type="macronutrient")
        protein_nutrient = Nutrient(name="Protein", unit="g", nutrient_type="macronutrient")
        fat_nutrient = Nutrient(name="Fat", unit="g", nutrient_type="macronutrient")
        
        db.add_all([carbs_nutrient, energy_nutrient, fiber_nutrient, protein_nutrient, fat_nutrient])
        db.flush()
        
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
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Successfully loaded {inserted_count} foods from enriched GI database with USDA nutritional data",
            "foods_loaded": inserted_count,
            "foods_skipped": skipped_count,
            "data_sources": "Foster-Powell 2002 (GI/GL) + USDA FoodData Central (Nutrients)"
        }
        
    except Exception as e:
        logger.error(f"Error loading GI database: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error loading GI database: {str(e)}"
        )


@router.get("/food-count")
def get_food_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of foods in database"""
    try:
        count = db.query(Food).count()
        return {"food_count": count}
    except Exception as e:
        logger.error(f"Error getting food count: {e}")
        raise HTTPException(status_code=500, detail=str(e))
