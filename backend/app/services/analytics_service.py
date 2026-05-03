"""
Analytics service for nutritional insights and reporting.

This service handles:
- Daily, weekly, and monthly nutritional summaries
- Average calorie calculations across time periods
- Macronutrient percentage distribution
- Carbohydrate intake warnings for diabetes management
- Nutritional trend analysis for visualization
"""

import logging
from typing import List, Tuple, Optional
from datetime import datetime, timedelta, date
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from decimal import Decimal

from app.models import FoodEntry, Food
from app.services.nutritional_calculator import NutritionalCalculator
from app.services.portion_converter import PortionConverter
from app.schemas.analytics import (
    PeriodSummaryResponse,
    MacronutrientDistribution,
    CarbohydrateWarning,
    NutritionalTrendsResponse,
    DailyTrendData
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and nutritional insights."""
    
    # Recommended daily carbohydrate intake for diabetes management (grams)
    # Based on ADA guidelines: 45-60g per meal, ~135-180g per day for moderate carb diet
    RECOMMENDED_DAILY_CARBS_G = 180.0
    
    # Warning thresholds
    MODERATE_WARNING_THRESHOLD = 1.15  # 15% above recommended
    HIGH_WARNING_THRESHOLD = 1.30      # 30% above recommended
    
    def __init__(self, db: Session):
        """
        Initialize the analytics service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.nutritional_calculator = NutritionalCalculator(db)
        self.portion_converter = PortionConverter()
    
    def get_period_summary(
        self,
        user_id: UUID,
        period: str,
        reference_date: date
    ) -> PeriodSummaryResponse:
        """
        Get nutritional summary for a time period (daily, weekly, monthly).
        
        Args:
            user_id: UUID of the user
            period: Period type ('daily', 'weekly', 'monthly')
            reference_date: Reference date for the period
            
        Returns:
            PeriodSummaryResponse with nutritional summary and warnings
            
        Raises:
            ValueError: If period is invalid
        """
        # Calculate date range based on period
        start_date, end_date = self._calculate_period_range(period, reference_date)
        
        # Get all entries in the period
        entries = self._get_entries_in_range(user_id, start_date, end_date)
        
        # Calculate nutritional totals
        total_nutrition = self._calculate_total_nutrition(entries)
        
        # Calculate number of days with data
        days_with_data = self._count_days_with_data(entries)
        
        # Calculate average daily calories
        avg_daily_calories = (
            total_nutrition['calories'] / days_with_data if days_with_data > 0 else 0.0
        )
        
        # Calculate macronutrient distribution
        macro_distribution = self._calculate_macronutrient_distribution(total_nutrition)
        
        # Check for carbohydrate warnings
        warnings = self._check_carbohydrate_warnings(user_id, start_date, end_date)
        
        logger.info(
            f"Generated {period} summary for user {user_id}: "
            f"{total_nutrition['calories']:.1f} total calories, "
            f"{avg_daily_calories:.1f} avg daily calories"
        )
        
        return PeriodSummaryResponse(
            period=period,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            total_calories=total_nutrition['calories'],
            avg_daily_calories=avg_daily_calories,
            total_protein_g=total_nutrition['protein_g'],
            total_carbohydrates_g=total_nutrition['carbohydrates_g'],
            total_fat_g=total_nutrition['fat_g'],
            total_fiber_g=total_nutrition['fiber_g'],
            macronutrient_distribution=macro_distribution,
            warnings=warnings,
            days_with_data=days_with_data
        )
    
    def calculate_average_calories(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date
    ) -> float:
        """
        Calculate average daily calorie intake over a date range.
        
        Args:
            user_id: UUID of the user
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            Average daily calories
        """
        entries = self._get_entries_in_range(user_id, start_date, end_date)
        total_nutrition = self._calculate_total_nutrition(entries)
        days_with_data = self._count_days_with_data(entries)
        
        if days_with_data == 0:
            return 0.0
        
        avg_calories = total_nutrition['calories'] / days_with_data
        
        logger.info(
            f"Calculated average calories for user {user_id}: "
            f"{avg_calories:.1f} kcal/day over {days_with_data} days"
        )
        
        return avg_calories
    
    def calculate_macronutrient_distribution(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date
    ) -> MacronutrientDistribution:
        """
        Calculate macronutrient distribution as percentages.
        
        Args:
            user_id: UUID of the user
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            MacronutrientDistribution with percentages
        """
        entries = self._get_entries_in_range(user_id, start_date, end_date)
        total_nutrition = self._calculate_total_nutrition(entries)
        
        distribution = self._calculate_macronutrient_distribution(total_nutrition)
        
        logger.info(
            f"Calculated macronutrient distribution for user {user_id}: "
            f"P:{distribution.protein_percent:.1f}% "
            f"C:{distribution.carbohydrates_percent:.1f}% "
            f"F:{distribution.fat_percent:.1f}%"
        )
        
        return distribution
    
    def check_carbohydrate_warnings(
        self,
        user_id: UUID,
        check_date: date
    ) -> Optional[CarbohydrateWarning]:
        """
        Check if carbohydrate intake exceeds recommended levels for a specific date.
        
        Args:
            user_id: UUID of the user
            check_date: Date to check
            
        Returns:
            CarbohydrateWarning if intake exceeds recommendations, None otherwise
        """
        warnings = self._check_carbohydrate_warnings(user_id, check_date, check_date)
        return warnings[0] if warnings else None
    
    def get_nutritional_trends(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date
    ) -> NutritionalTrendsResponse:
        """
        Get nutritional trends over a date range for visualization.
        
        Args:
            user_id: UUID of the user
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            NutritionalTrendsResponse with daily data and averages
        """
        # Get daily summaries for each date in range
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            entries = self._get_entries_in_range(
                user_id,
                current_date,
                current_date
            )
            
            if entries:  # Only include days with data
                nutrition = self._calculate_total_nutrition(entries)
                daily_data.append(DailyTrendData(
                    date=current_date.strftime('%Y-%m-%d'),
                    calories=nutrition['calories'],
                    protein_g=nutrition['protein_g'],
                    carbohydrates_g=nutrition['carbohydrates_g'],
                    fat_g=nutrition['fat_g'],
                    fiber_g=nutrition['fiber_g']
                ))
            
            current_date += timedelta(days=1)
        
        # Calculate averages
        if daily_data:
            avg_calories = sum(d.calories for d in daily_data) / len(daily_data)
            avg_protein = sum(d.protein_g for d in daily_data) / len(daily_data)
            avg_carbs = sum(d.carbohydrates_g for d in daily_data) / len(daily_data)
            avg_fat = sum(d.fat_g for d in daily_data) / len(daily_data)
        else:
            avg_calories = avg_protein = avg_carbs = avg_fat = 0.0
        
        logger.info(
            f"Generated nutritional trends for user {user_id}: "
            f"{len(daily_data)} days of data, avg {avg_calories:.1f} kcal/day"
        )
        
        return NutritionalTrendsResponse(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            daily_data=daily_data,
            avg_calories=avg_calories,
            avg_protein_g=avg_protein,
            avg_carbohydrates_g=avg_carbs,
            avg_fat_g=avg_fat
        )
    
    def _calculate_period_range(
        self,
        period: str,
        reference_date: date
    ) -> Tuple[date, date]:
        """
        Calculate start and end dates for a period.
        
        Args:
            period: Period type ('daily', 'weekly', 'monthly')
            reference_date: Reference date
            
        Returns:
            Tuple of (start_date, end_date)
            
        Raises:
            ValueError: If period is invalid
        """
        if period == 'daily':
            return reference_date, reference_date
        
        elif period == 'weekly':
            # Week starts on Monday (weekday 0)
            days_since_monday = reference_date.weekday()
            start_date = reference_date - timedelta(days=days_since_monday)
            end_date = start_date + timedelta(days=6)
            return start_date, end_date
        
        elif period == 'monthly':
            # Month from 1st to last day
            start_date = reference_date.replace(day=1)
            # Get last day of month
            if reference_date.month == 12:
                next_month = reference_date.replace(year=reference_date.year + 1, month=1, day=1)
            else:
                next_month = reference_date.replace(month=reference_date.month + 1, day=1)
            end_date = next_month - timedelta(days=1)
            return start_date, end_date
        
        else:
            raise ValueError(f"Invalid period: {period}. Must be 'daily', 'weekly', or 'monthly'")
    
    def _get_entries_in_range(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[FoodEntry]:
        """
        Get all food entries for a user in a date range.
        
        Args:
            user_id: UUID of the user
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of FoodEntry objects
        """
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        entries = self.db.query(FoodEntry).filter(
            FoodEntry.user_id == user_id,
            FoodEntry.consumed_at >= start_datetime,
            FoodEntry.consumed_at <= end_datetime
        ).all()
        
        return entries
    
    def _calculate_total_nutrition(self, entries: List[FoodEntry]) -> dict:
        """
        Calculate total nutritional values for a list of entries.
        
        Args:
            entries: List of FoodEntry objects
            
        Returns:
            Dictionary with total nutritional values
        """
        total_nutrition = self.nutritional_calculator._empty_nutrition_dict()
        
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
        
        return total_nutrition
    
    def _count_days_with_data(self, entries: List[FoodEntry]) -> int:
        """
        Count the number of unique days with food entries.
        
        Args:
            entries: List of FoodEntry objects
            
        Returns:
            Number of unique days
        """
        if not entries:
            return 0
        
        unique_dates = set(entry.consumed_at.date() for entry in entries)
        return len(unique_dates)
    
    def _calculate_macronutrient_distribution(
        self,
        nutrition: dict
    ) -> MacronutrientDistribution:
        """
        Calculate macronutrient distribution as percentages.
        
        Macronutrients contribute to calories as follows:
        - Protein: 4 calories per gram
        - Carbohydrates: 4 calories per gram
        - Fat: 9 calories per gram
        
        Args:
            nutrition: Dictionary with nutritional values
            
        Returns:
            MacronutrientDistribution with percentages
        """
        # Calculate calories from each macronutrient
        protein_calories = nutrition['protein_g'] * 4
        carb_calories = nutrition['carbohydrates_g'] * 4
        fat_calories = nutrition['fat_g'] * 9
        
        total_macro_calories = protein_calories + carb_calories + fat_calories
        
        # Calculate percentages (handle division by zero)
        if total_macro_calories > 0:
            protein_percent = (protein_calories / total_macro_calories) * 100
            carb_percent = (carb_calories / total_macro_calories) * 100
            fat_percent = (fat_calories / total_macro_calories) * 100
        else:
            protein_percent = carb_percent = fat_percent = 0.0
        
        return MacronutrientDistribution(
            protein_percent=round(protein_percent, 1),
            carbohydrates_percent=round(carb_percent, 1),
            fat_percent=round(fat_percent, 1)
        )
    
    def _check_carbohydrate_warnings(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[CarbohydrateWarning]:
        """
        Check for carbohydrate intake warnings in a date range.
        
        Args:
            user_id: UUID of the user
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of CarbohydrateWarning objects
        """
        warnings = []
        current_date = start_date
        
        while current_date <= end_date:
            # Get entries for this day
            entries = self._get_entries_in_range(user_id, current_date, current_date)
            
            if entries:
                nutrition = self._calculate_total_nutrition(entries)
                carbs = nutrition['carbohydrates_g']
                
                # Check if carbs exceed recommended level
                if carbs > self.RECOMMENDED_DAILY_CARBS_G:
                    excess_percent = ((carbs / self.RECOMMENDED_DAILY_CARBS_G) - 1) * 100
                    
                    # Determine severity
                    if carbs >= self.RECOMMENDED_DAILY_CARBS_G * self.HIGH_WARNING_THRESHOLD:
                        severity = 'high'
                        message = (
                            f"Carbohydrate intake is {excess_percent:.1f}% above recommended level. "
                            f"Consider reducing carb intake for better diabetes management."
                        )
                    elif carbs >= self.RECOMMENDED_DAILY_CARBS_G * self.MODERATE_WARNING_THRESHOLD:
                        severity = 'moderate'
                        message = (
                            f"Carbohydrate intake is {excess_percent:.1f}% above recommended level "
                            f"for diabetes management."
                        )
                    else:
                        # Slightly above but not enough for a warning
                        current_date += timedelta(days=1)
                        continue
                    
                    warnings.append(CarbohydrateWarning(
                        date=current_date.strftime('%Y-%m-%d'),
                        carbohydrates_g=round(carbs, 1),
                        recommended_max_g=self.RECOMMENDED_DAILY_CARBS_G,
                        severity=severity,
                        message=message
                    ))
            
            current_date += timedelta(days=1)
        
        return warnings
    
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
