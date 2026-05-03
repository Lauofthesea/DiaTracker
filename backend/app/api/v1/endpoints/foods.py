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
