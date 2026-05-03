"""
Food entry service for managing user meal tracking.

This service handles:
- Creating food entries with nutritional calculations
- Retrieving food entries with filtering
- Updating food entries (with 7-day restriction)
- Deleting food entries (with 7-day restriction)
- Calculating daily nutritional summaries
"""

import logging
from typing import List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract
from decimal import Decimal

from app.models import FoodEntry, Food, User
from app.services.nutritional_calculator import NutritionalCalculator
from app.services.portion_converter import PortionConverter
from app.schemas.food_entry import (
    FoodEntryCreate,
    FoodEntryUpdate,
    FoodEntryResponse,
    NutritionalTotals,
    DailyNutritionalSummary
)

logger = logging.getLogger(__name__)


class FoodEntryService:
    """Service for food entry operations."""
    
    # 7-day edit window in days
    EDIT_WINDOW_DAYS = 7
    
    def __init__(self, db: Session):
        """
        Initialize the food entry service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.nutritional_calculator = NutritionalCalculator(db)
        self.portion_converter = PortionConverter()
    
    def create_food_entry(
        self,
        user_id: UUID,
        entry_data: FoodEntryCreate
    ) -> FoodEntryResponse:
        """
        Create a new food entry with nutritional calculations.
        
        Args:
            user_id: UUID of the user
            entry_data: Food entry creation data
            
        Returns:
            Created food entry with nutritional totals
            
        Raises:
            ValueError: If food not found or invalid data
        """
        # Verify food exists
        food = self.db.query(Food).filter(Food.food_id == entry_data.food_id).first()
        if not food:
            raise ValueError(f"Food with ID {entry_data.food_id} not found")
        
        # Convert quantity to grams for nutritional calculation
        quantity_grams = self._convert_to_grams(
            float(entry_data.quantity),
            entry_data.unit,
            food.category
        )
        
        # Calculate nutritional values
        nutritional_data = self.nutritional_calculator.calculate_food_nutrition(
            entry_data.food_id,
            quantity_grams
        )
        
        # Create food entry
        food_entry = FoodEntry(
            user_id=user_id,
            food_id=entry_data.food_id,
            quantity=entry_data.quantity,
            unit=entry_data.unit,
            meal_type=entry_data.meal_type,
            consumed_at=entry_data.consumed_at
        )
        
        self.db.add(food_entry)
        self.db.commit()
        self.db.refresh(food_entry)
        
        logger.info(
            f"Created food entry {food_entry.entry_id} for user {user_id}: "
            f"{food.name} ({entry_data.quantity} {entry_data.unit})"
        )
        
        # Build response
        return self._build_entry_response(food_entry, food, nutritional_data)
    
    def get_food_entries(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        meal_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[FoodEntryResponse], int]:
        """
        Get food entries for a user with filtering and pagination.
        
        Args:
            user_id: UUID of the user
            start_date: Filter entries from this date (inclusive)
            end_date: Filter entries until this date (inclusive)
            meal_type: Filter by meal type
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (list of food entries, total count)
        """
        # Build query
        query = self.db.query(FoodEntry).filter(FoodEntry.user_id == user_id)
        
        # Apply date filters
        if start_date:
            query = query.filter(FoodEntry.consumed_at >= start_date)
        if end_date:
            # Include the entire end date (until 23:59:59)
            end_of_day = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(FoodEntry.consumed_at <= end_of_day)
        
        # Apply meal type filter
        if meal_type:
            query = query.filter(FoodEntry.meal_type == meal_type.lower())
        
        # Order by consumed_at descending (most recent first)
        query = query.order_by(FoodEntry.consumed_at.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        entries = query.offset(offset).limit(page_size).all()
        
        # Build responses with nutritional data
        responses = []
        for entry in entries:
            # Get food details
            food = self.db.query(Food).filter(Food.food_id == entry.food_id).first()
            
            # Calculate nutritional values
            quantity_grams = self._convert_to_grams(
                float(entry.quantity),
                entry.unit,
                food.category if food else None
            )
            nutritional_data = self.nutritional_calculator.calculate_food_nutrition(
                entry.food_id,
                quantity_grams
            )
            
            response = self._build_entry_response(entry, food, nutritional_data)
            responses.append(response)
        
        logger.info(
            f"Retrieved {len(responses)} food entries for user {user_id} "
            f"(page {page}, total {total})"
        )
        
        return responses, total
    
    def update_food_entry(
        self,
        entry_id: UUID,
        user_id: UUID,
        update_data: FoodEntryUpdate
    ) -> FoodEntryResponse:
        """
        Update a food entry (only if within 7-day edit window).
        
        Args:
            entry_id: UUID of the food entry
            user_id: UUID of the user (for authorization)
            update_data: Updated food entry data
            
        Returns:
            Updated food entry with nutritional totals
            
        Raises:
            ValueError: If entry not found, unauthorized, or outside edit window
        """
        # Get entry
        entry = self.db.query(FoodEntry).filter(
            FoodEntry.entry_id == entry_id,
            FoodEntry.user_id == user_id
        ).first()
        
        if not entry:
            raise ValueError(f"Food entry {entry_id} not found or unauthorized")
        
        # Check 7-day edit window
        if not self._is_within_edit_window(entry.consumed_at):
            raise ValueError(
                f"Cannot edit entries older than {self.EDIT_WINDOW_DAYS} days. "
                f"This entry was consumed on {entry.consumed_at.date()}"
            )
        
        # Update fields
        if update_data.quantity is not None:
            entry.quantity = update_data.quantity
        if update_data.unit is not None:
            entry.unit = update_data.unit
        if update_data.meal_type is not None:
            entry.meal_type = update_data.meal_type
        
        self.db.commit()
        self.db.refresh(entry)
        
        # Get food details
        food = self.db.query(Food).filter(Food.food_id == entry.food_id).first()
        
        # Recalculate nutritional values
        quantity_grams = self._convert_to_grams(
            float(entry.quantity),
            entry.unit,
            food.category if food else None
        )
        nutritional_data = self.nutritional_calculator.calculate_food_nutrition(
            entry.food_id,
            quantity_grams
        )
        
        logger.info(f"Updated food entry {entry_id} for user {user_id}")
        
        return self._build_entry_response(entry, food, nutritional_data)
    
    def delete_food_entry(
        self,
        entry_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a food entry (only if within 7-day edit window).
        
        Args:
            entry_id: UUID of the food entry
            user_id: UUID of the user (for authorization)
            
        Returns:
            True if deleted successfully
            
        Raises:
            ValueError: If entry not found, unauthorized, or outside edit window
        """
        # Get entry
        entry = self.db.query(FoodEntry).filter(
            FoodEntry.entry_id == entry_id,
            FoodEntry.user_id == user_id
        ).first()
        
        if not entry:
            raise ValueError(f"Food entry {entry_id} not found or unauthorized")
        
        # Check 7-day edit window
        if not self._is_within_edit_window(entry.consumed_at):
            raise ValueError(
                f"Cannot delete entries older than {self.EDIT_WINDOW_DAYS} days. "
                f"This entry was consumed on {entry.consumed_at.date()}"
            )
        
        self.db.delete(entry)
        self.db.commit()
        
        logger.info(f"Deleted food entry {entry_id} for user {user_id}")
        
        return True
    
    def get_daily_summary(
        self,
        user_id: UUID,
        date: datetime
    ) -> DailyNutritionalSummary:
        """
        Get daily nutritional summary for a specific date.
        
        Args:
            user_id: UUID of the user
            date: Date to get summary for
            
        Returns:
            Daily nutritional summary with meal breakdown
        """
        # Get all entries for the date
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        entries = self.db.query(FoodEntry).filter(
            FoodEntry.user_id == user_id,
            FoodEntry.consumed_at >= start_of_day,
            FoodEntry.consumed_at <= end_of_day
        ).all()
        
        # Calculate totals
        total_nutrition = self.nutritional_calculator._empty_nutrition_dict()
        meal_breakdown = {}
        
        for entry in entries:
            # Get food details
            food = self.db.query(Food).filter(Food.food_id == entry.food_id).first()
            
            # Calculate nutritional values
            quantity_grams = self._convert_to_grams(
                float(entry.quantity),
                entry.unit,
                food.category if food else None
            )
            nutrition = self.nutritional_calculator.calculate_food_nutrition(
                entry.food_id,
                quantity_grams
            )
            
            # Add to total
            total_nutrition = self.nutritional_calculator._sum_nutrition(
                total_nutrition,
                nutrition
            )
            
            # Add to meal breakdown
            meal_type = entry.meal_type
            if meal_type not in meal_breakdown:
                meal_breakdown[meal_type] = self.nutritional_calculator._empty_nutrition_dict()
            
            meal_breakdown[meal_type] = self.nutritional_calculator._sum_nutrition(
                meal_breakdown[meal_type],
                nutrition
            )
        
        # Convert meal breakdown to NutritionalTotals
        meal_breakdown_response = {}
        for meal_type, nutrition in meal_breakdown.items():
            meal_breakdown_response[meal_type] = NutritionalTotals(**nutrition)
        
        return DailyNutritionalSummary(
            date=date.strftime('%Y-%m-%d'),
            total_calories=total_nutrition['calories'],
            total_protein_g=total_nutrition['protein_g'],
            total_carbohydrates_g=total_nutrition['carbohydrates_g'],
            total_fat_g=total_nutrition['fat_g'],
            total_fiber_g=total_nutrition['fiber_g'],
            meal_breakdown=meal_breakdown_response
        )
    
    def _is_within_edit_window(self, consumed_at: datetime) -> bool:
        """
        Check if a food entry is within the 7-day edit window.
        
        Args:
            consumed_at: When the food was consumed
            
        Returns:
            True if within edit window, False otherwise
        """
        now = datetime.now(timezone.utc)
        
        # Make consumed_at timezone-aware if it isn't
        if consumed_at.tzinfo is None:
            consumed_at = consumed_at.replace(tzinfo=timezone.utc)
        
        age = now - consumed_at
        return age.days < self.EDIT_WINDOW_DAYS
    
    def _convert_to_grams(
        self,
        quantity: float,
        unit: str,
        food_category: Optional[str] = None
    ) -> float:
        """
        Convert quantity to grams for nutritional calculation.
        
        Args:
            quantity: Amount in the given unit
            unit: Unit of measurement
            food_category: Food category (for density estimation)
            
        Returns:
            Quantity in grams
        """
        unit_lower = unit.lower().strip()
        
        # Already in grams
        if unit_lower in ['g', 'gram', 'grams']:
            return quantity
        
        # Try to convert to grams
        try:
            return self.portion_converter.convert(
                quantity,
                unit,
                'g',
                food_density=None  # Use default density
            )
        except ValueError as e:
            logger.warning(
                f"Could not convert {quantity} {unit} to grams: {e}. "
                f"Using quantity as-is."
            )
            # If conversion fails, assume the quantity is already in grams
            return quantity
    
    def _build_entry_response(
        self,
        entry: FoodEntry,
        food: Optional[Food],
        nutritional_data: dict
    ) -> FoodEntryResponse:
        """
        Build a FoodEntryResponse from database models and nutritional data.
        
        Args:
            entry: FoodEntry database model
            food: Food database model (or None)
            nutritional_data: Nutritional data dictionary
            
        Returns:
            FoodEntryResponse schema
        """
        return FoodEntryResponse(
            entry_id=entry.entry_id,
            user_id=entry.user_id,
            food_id=entry.food_id,
            food_name=food.name if food else "Unknown Food",
            quantity=entry.quantity,
            unit=entry.unit,
            meal_type=entry.meal_type,
            consumed_at=entry.consumed_at,
            created_at=entry.created_at,
            nutritional_totals=NutritionalTotals(**nutritional_data)
        )
