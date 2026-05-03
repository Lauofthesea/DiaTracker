"""
Profile API endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.profile import (
    ProfileResponse,
    ProfileUpdate,
    HealthMetricsHistoryResponse
)
from app.services.profile_service import ProfileService

router = APIRouter()


@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile.
    
    Returns user profile with current health metrics.
    """
    user_id = current_user.user_id
    return ProfileService.get_profile(db, user_id)


@router.put("", response_model=ProfileResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile.
    
    Updates profile fields including allergen preferences,
    dietary restrictions, and health conditions.
    """
    user_id = current_user.user_id
    return ProfileService.update_profile(db, user_id, profile_data)


@router.get("/health-metrics-history", response_model=HealthMetricsHistoryResponse)
def get_health_metrics_history(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get health metrics history with pagination.
    
    Returns historical health metrics ordered by recorded_at descending,
    with associated predictions if available.
    """
    user_id = current_user.user_id
    return ProfileService.get_health_metrics_history(db, user_id, page, page_size)
