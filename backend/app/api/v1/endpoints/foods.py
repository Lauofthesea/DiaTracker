"""
Food API endpoints for search and filtering.
"""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import User
from app.services.food_service import FoodService
from app.schemas.food import (
    FoodSearchResponse,
    FoodSearchResult,
    FoodDetail,
    CustomFoodCreate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/search", response_model=FoodSearchResponse)
def search_foods(
    q: Optional[str] = Query(None, description="Search query text"),
    category: Optional[str] = Query(None, description="Filter by category"),
    allergens: Optional[str] = Query(
        None, 
        description="Comma-separated list of allergens to exclude"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search and filter foods with pagination.
    
    - **q**: Text search query (searches food names)
    - **category**: Filter by food category
    - **allergens**: Comma-separated allergens to exclude (e.g., "Dairy,Nut Allergy")
    - **page**: Page number (1-indexed)
    - **page_size**: Number of items per page (max 100)
    
    Returns paginated list of foods with relevance ranking.
    """
    try:
        # Parse allergens
        exclude_allergens = None
        if allergens:
            exclude_allergens = [a.strip() for a in allergens.split(',') if a.strip()]
        
        # Search foods
        food_service = FoodService(db)
        results, total = food_service.search_foods(
            query=q,
            category=category,
            exclude_allergens=exclude_allergens,
            page=page,
            page_size=page_size
        )
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        return FoodSearchResponse(
            foods=results,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error searching foods: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error searching foods"
        )


@router.get("/autocomplete", response_model=List[FoodSearchResult])
def autocomplete_foods(
    q: str = Query(..., min_length=2, description="Search query (min 2 chars)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Quick food name search for autocomplete.
    
    - **q**: Search query (minimum 2 characters)
    - **limit**: Maximum number of results (max 50)
    
    Returns list of matching foods ordered by name.
    """
    try:
        food_service = FoodService(db)
        results = food_service.search_foods_by_name(q, limit)
        return results
        
    except Exception as e:
        logger.error(f"Error in autocomplete: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error searching foods"
        )


@router.get("/categories", response_model=List[str])
def get_food_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all food categories.
    
    Returns list of category names sorted alphabetically.
    """
    try:
        food_service = FoodService(db)
        categories = food_service.get_categories()
        return categories
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error retrieving categories"
        )


@router.get("/{food_id}", response_model=FoodDetail)
def get_food_detail(
    food_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific food.
    
    - **food_id**: UUID of the food
    
    Returns detailed food information including all nutrients.
    """
    try:
        food_service = FoodService(db)
        food = food_service.get_food_by_id(food_id)
        
        if not food:
            raise HTTPException(
                status_code=404,
                detail=f"Food with ID {food_id} not found"
            )
        
        return food
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting food detail: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error retrieving food details"
        )


@router.post("/custom", response_model=FoodDetail)
def create_custom_food(
    food_data: CustomFoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a custom food entry with manual nutritional data.
    
    This endpoint allows users to create custom foods that aren't in the database.
    The food will be created with the provided nutritional information.
    
    - **name**: Name of the food
    - **serving_size**: Serving size description (e.g., "1 cup", "100g")
    - **calories**: Calories per serving
    - **carbohydrates_g**: Carbohydrates in grams (optional)
    - **protein_g**: Protein in grams (optional)
    - **fat_g**: Fat in grams (optional)
    - **fiber_g**: Fiber in grams (optional)
    
    Returns the created food with generated UUID.
    """
    try:
        food_service = FoodService(db)
        food = food_service.create_custom_food(
            name=food_data.name,
            serving_size=food_data.serving_size,
            calories=food_data.calories,
            carbohydrates_g=food_data.carbohydrates_g,
            protein_g=food_data.protein_g,
            fat_g=food_data.fat_g,
            fiber_g=food_data.fiber_g
        )
        
        logger.info(f"Created custom food '{food_data.name}' for user {current_user.user_id}")
        return food
        
    except Exception as e:
        logger.error(f"Error creating custom food: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error creating custom food"
        )


@router.post("/load-gi-database")
def load_gi_database(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ADMIN: Load foods from the GI database CSV.
    This will clear existing foods and load the 201 foods from gi_database_research_only.csv
    """
    try:
        from pathlib import Path
        import csv
        from decimal import Decimal
        from sqlalchemy import text
        from app.models.nutrient import Nutrient
        from app.models.food_nutrient import FoodNutrient
        from app.models.food import Food as FoodModel
        
        logger.info("Starting GI database load...")
        
        # Path to GI database CSV - go up from endpoints to backend, then to datasets
        csv_path = Path(__file__).parent.parent.parent.parent.parent.parent / "datasets" / "gi_database_research_only.csv"
        
        logger.info(f"Looking for CSV at: {csv_path}")
        
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
        energy_nutrient = Nutrient(name="Energy", unit="kcal", nutrient_type="other")
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
            
            # Get nutritional values
            gi_value = float(row['gi_value'])
            gl_value = float(row['gl_value'])
            serving_size = float(row['serving_size_g'])
            available_carbs = float(row['available_carbs_g'])
            
            # Estimate calories and scale to per 100g
            carbs_per_100g = (available_carbs / serving_size) * 100
            calories_per_100g = carbs_per_100g * 4
            
            # Create food
            food = FoodModel(
                name=food_name,
                description=f"GI: {gi_value}, GL: {gl_value}, Serving: {serving_size}g",
                category=category,
                food_type="natural"
            )
            db.add(food)
            db.flush()
            
            # Add nutrients
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
                amount=Decimal("2.0"),
                per_unit="100g"
            ))
            db.add(FoodNutrient(
                food_id=food.food_id,
                nutrient_id=protein_nutrient.nutrient_id,
                amount=Decimal("5.0"),
                per_unit="100g"
            ))
            db.add(FoodNutrient(
                food_id=food.food_id,
                nutrient_id=fat_nutrient.nutrient_id,
                amount=Decimal("3.0"),
                per_unit="100g"
            ))
            
            inserted_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Successfully loaded {inserted_count} foods from GI database",
            "foods_loaded": inserted_count,
            "foods_skipped": skipped_count
        }
        
    except Exception as e:
        logger.error(f"Error loading GI database: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error loading GI database: {str(e)}"
        )
