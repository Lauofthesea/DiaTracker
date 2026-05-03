"""
Analytics API endpoints for nutritional insights and reporting.
"""

import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import User
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    PeriodSummaryResponse,
    MacronutrientDistribution,
    CarbohydrateWarning,
    NutritionalTrendsResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary", response_model=PeriodSummaryResponse)
def get_period_summary(
    period: str = Query(
        ...,
        description="Period type: 'daily', 'weekly', or 'monthly'"
    ),
    date: date = Query(
        ...,
        description="Reference date for the period (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get nutritional summary for a time period.
    
    - **period**: Period type ('daily', 'weekly', 'monthly')
    - **date**: Reference date for the period
    
    Returns summary with:
    - Total and average daily calories
    - Macronutrient totals and distribution
    - Carbohydrate warnings for diabetes management
    - Number of days with data
    
    **Period Definitions:**
    - daily: The specified date
    - weekly: Monday-Sunday week containing the specified date
    - monthly: Calendar month containing the specified date
    """
    try:
        # Validate period
        if period not in ['daily', 'weekly', 'monthly']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="period must be 'daily', 'weekly', or 'monthly'"
            )
        
        service = AnalyticsService(db)
        summary = service.get_period_summary(
            user_id=current_user.user_id,
            period=period,
            reference_date=date
        )
        
        return summary
        
    except ValueError as e:
        logger.warning(f"Validation error in period summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting period summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving period summary"
        )


@router.get("/trends", response_model=NutritionalTrendsResponse)
def get_nutritional_trends(
    start_date: date = Query(
        ...,
        description="Start date for trends (YYYY-MM-DD)"
    ),
    end_date: date = Query(
        ...,
        description="End date for trends (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get nutritional trends over a date range for visualization.
    
    - **start_date**: Start date (inclusive)
    - **end_date**: End date (inclusive)
    
    Returns:
    - Daily nutritional data for each day with food entries
    - Average daily values across the period
    
    **Note**: Only days with food entries are included in the daily_data array.
    Days without entries are omitted from the response.
    """
    try:
        # Validate date range
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be before or equal to end_date"
            )
        
        # Limit to reasonable date ranges (e.g., 1 year)
        days_diff = (end_date - start_date).days
        if days_diff > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date range cannot exceed 365 days"
            )
        
        service = AnalyticsService(db)
        trends = service.get_nutritional_trends(
            user_id=current_user.user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return trends
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting nutritional trends: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving nutritional trends"
        )


@router.get("/average-calories", response_model=float)
def get_average_calories(
    start_date: date = Query(
        ...,
        description="Start date (YYYY-MM-DD)"
    ),
    end_date: date = Query(
        ...,
        description="End date (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate average daily calorie intake over a date range.
    
    - **start_date**: Start date (inclusive)
    - **end_date**: End date (inclusive)
    
    Returns the average daily calories as a float.
    """
    try:
        # Validate date range
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be before or equal to end_date"
            )
        
        service = AnalyticsService(db)
        avg_calories = service.calculate_average_calories(
            user_id=current_user.user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return avg_calories
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating average calories: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating average calories"
        )


@router.get("/macronutrient-distribution", response_model=MacronutrientDistribution)
def get_macronutrient_distribution(
    start_date: date = Query(
        ...,
        description="Start date (YYYY-MM-DD)"
    ),
    end_date: date = Query(
        ...,
        description="End date (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate macronutrient distribution as percentages.
    
    - **start_date**: Start date (inclusive)
    - **end_date**: End date (inclusive)
    
    Returns percentages of calories from protein, carbohydrates, and fat.
    Percentages sum to 100% (within rounding tolerance).
    """
    try:
        # Validate date range
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be before or equal to end_date"
            )
        
        service = AnalyticsService(db)
        distribution = service.calculate_macronutrient_distribution(
            user_id=current_user.user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return distribution
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating macronutrient distribution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating macronutrient distribution"
        )


@router.get("/carbohydrate-warning", response_model=CarbohydrateWarning | None)
def get_carbohydrate_warning(
    date: date = Query(
        ...,
        description="Date to check (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if carbohydrate intake exceeds recommended levels for a specific date.
    
    - **date**: Date to check
    
    Returns a CarbohydrateWarning if intake exceeds recommendations, or null if within limits.
    
    **Diabetes Management Guidelines:**
    - Recommended daily carbohydrate intake: 180g
    - Moderate warning: 15% above recommended (207g)
    - High warning: 30% above recommended (234g)
    """
    try:
        service = AnalyticsService(db)
        warning = service.check_carbohydrate_warnings(
            user_id=current_user.user_id,
            check_date=date
        )
        
        return warning
        
    except Exception as e:
        logger.error(f"Error checking carbohydrate warning: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking carbohydrate warning"
        )
