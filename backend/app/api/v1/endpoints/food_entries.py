"""
Food entry API endpoints for meal tracking.
"""

import logging
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import User
from app.services.food_entry_service import FoodEntryService
from app.schemas.food_entry import (
    FoodEntryCreate,
    FoodEntryUpdate,
    FoodEntryResponse,
    FoodEntryListResponse,
    DailyNutritionalSummary
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=FoodEntryResponse, status_code=status.HTTP_201_CREATED)
def create_food_entry(
    entry_data: FoodEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new food entry.
    
    - **food_id**: UUID of the food item from the food database
    - **quantity**: Amount consumed (must be positive)
    - **unit**: Unit of measurement (g, oz, cup, tbsp, etc.)
    - **meal_type**: Type of meal (breakfast, lunch, dinner, snack)
    - **consumed_at**: Timestamp when the food was consumed
    
    Returns the created food entry with calculated nutritional totals.
    """
    try:
        service = FoodEntryService(db)
        entry = service.create_food_entry(current_user.user_id, entry_data)
        return entry
        
    except ValueError as e:
        logger.warning(f"Validation error creating food entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating food entry: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating food entry"
        )


@router.get("", response_model=FoodEntryListResponse)
def get_food_entries(
    start_date: Optional[datetime] = Query(
        None,
        description="Filter entries from this date (ISO 8601 format)"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter entries until this date (ISO 8601 format)"
    ),
    meal_type: Optional[str] = Query(
        None,
        description="Filter by meal type (breakfast, lunch, dinner, snack)"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get food entries for the current user with filtering and pagination.
    
    - **start_date**: Filter entries from this date (inclusive)
    - **end_date**: Filter entries until this date (inclusive)
    - **meal_type**: Filter by meal type
    - **page**: Page number (1-indexed)
    - **page_size**: Number of items per page (max 100)
    
    Returns paginated list of food entries with nutritional totals.
    """
    try:
        # Validate meal type if provided
        if meal_type:
            allowed_meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
            if meal_type.lower() not in allowed_meal_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"meal_type must be one of: {', '.join(allowed_meal_types)}"
                )
        
        service = FoodEntryService(db)
        entries, total = service.get_food_entries(
            user_id=current_user.user_id,
            start_date=start_date,
            end_date=end_date,
            meal_type=meal_type,
            page=page,
            page_size=page_size
        )
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        return FoodEntryListResponse(
            entries=entries,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving food entries: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving food entries"
        )


@router.get("/daily-summary", response_model=DailyNutritionalSummary)
def get_daily_summary(
    date: datetime = Query(
        ...,
        description="Date to get summary for (ISO 8601 format, e.g., 2024-01-15)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get daily nutritional summary for a specific date.
    
    - **date**: Date to get summary for (time component is ignored)
    
    Returns total nutritional values for the day with breakdown by meal type.
    """
    try:
        service = FoodEntryService(db)
        summary = service.get_daily_summary(current_user.user_id, date)
        return summary
        
    except Exception as e:
        logger.error(f"Error getting daily summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving daily summary"
        )


@router.put("/{entry_id}", response_model=FoodEntryResponse)
def update_food_entry(
    entry_id: UUID,
    update_data: FoodEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a food entry (only if within 7-day edit window).
    
    - **entry_id**: UUID of the food entry to update
    - **quantity**: Updated quantity (optional)
    - **unit**: Updated unit (optional)
    - **meal_type**: Updated meal type (optional)
    
    Returns the updated food entry with recalculated nutritional totals.
    
    **Note**: Entries older than 7 days cannot be edited.
    """
    try:
        service = FoodEntryService(db)
        entry = service.update_food_entry(entry_id, current_user.user_id, update_data)
        return entry
        
    except ValueError as e:
        logger.warning(f"Validation error updating food entry: {e}")
        # Check if it's an edit window error
        if "older than" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating food entry: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating food entry"
        )


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a food entry (only if within 7-day edit window).
    
    - **entry_id**: UUID of the food entry to delete
    
    **Note**: Entries older than 7 days cannot be deleted.
    """
    try:
        service = FoodEntryService(db)
        service.delete_food_entry(entry_id, current_user.user_id)
        return None
        
    except ValueError as e:
        logger.warning(f"Validation error deleting food entry: {e}")
        # Check if it's an edit window error
        if "older than" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting food entry: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting food entry"
        )
