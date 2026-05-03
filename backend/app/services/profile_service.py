"""
Profile service for user profile management.
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from fastapi import HTTPException, status
from math import ceil

from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.health_metrics import HealthMetrics
from app.models.prediction import Prediction
from app.schemas.profile import (
    ProfileUpdate,
    ProfileResponse,
    CurrentHealthMetrics,
    HealthMetricsHistoryResponse,
    HealthMetricsHistoryItem
)


class ProfileService:
    """Service for handling user profile operations."""
    
    @staticmethod
    def create_profile_if_not_exists(db: Session, user_id: str) -> UserProfile:
        """
        Create user profile if it doesn't exist.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            
        Returns:
            UserProfile object
        """
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                allergen_preferences=[],
                dietary_restrictions=[],
                health_conditions=[]
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        return profile
    
    @staticmethod
    def get_profile(db: Session, user_id: str) -> ProfileResponse:
        """
        Get user profile with current health metrics.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            
        Returns:
            ProfileResponse with user info and current health metrics
            
        Raises:
            HTTPException: If user not found
        """
        # Get user with profile
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create profile if it doesn't exist
        profile = ProfileService.create_profile_if_not_exists(db, user_id)
        
        # Get latest health metrics
        latest_metrics = (
            db.query(HealthMetrics)
            .filter(HealthMetrics.user_id == user_id)
            .order_by(desc(HealthMetrics.recorded_at))
            .first()
        )
        
        # Build current health metrics if available
        current_health_metrics = None
        if latest_metrics:
            current_health_metrics = CurrentHealthMetrics(
                weight_kg=float(latest_metrics.weight_kg),
                blood_sugar_mgdl=float(latest_metrics.blood_sugar_mgdl),
                age=latest_metrics.age,
                height_cm=float(latest_metrics.height_cm),
                bmi=float(latest_metrics.bmi) if latest_metrics.bmi else 0.0,
                recorded_at=latest_metrics.recorded_at
            )
        
        # Build profile response
        return ProfileResponse(
            user_id=str(user.user_id),
            name=user.name,
            email=user.email,
            allergen_preferences=profile.allergen_preferences,
            dietary_restrictions=profile.dietary_restrictions,
            health_conditions=profile.health_conditions,
            current_health_metrics=current_health_metrics,
            created_at=user.created_at,
            last_login=user.last_login
        )
    
    @staticmethod
    def update_profile(
        db: Session,
        user_id: str,
        profile_data: ProfileUpdate
    ) -> ProfileResponse:
        """
        Update user profile.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            profile_data: Profile update data
            
        Returns:
            Updated ProfileResponse
            
        Raises:
            HTTPException: If user not found or update fails
        """
        # Get user
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create profile if it doesn't exist
        profile = ProfileService.create_profile_if_not_exists(db, user_id)
        
        try:
            # Update user name if provided
            if profile_data.name is not None:
                user.name = profile_data.name
            
            # Update profile fields if provided
            if profile_data.allergen_preferences is not None:
                profile.allergen_preferences = profile_data.allergen_preferences
            
            if profile_data.dietary_restrictions is not None:
                profile.dietary_restrictions = profile_data.dietary_restrictions
            
            if profile_data.health_conditions is not None:
                profile.health_conditions = profile_data.health_conditions
            
            db.commit()
            db.refresh(user)
            db.refresh(profile)
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update profile: {str(e)}"
            )
        
        # Return updated profile
        return ProfileService.get_profile(db, user_id)
    
    @staticmethod
    def get_health_metrics_history(
        db: Session,
        user_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> HealthMetricsHistoryResponse:
        """
        Get health metrics history with pagination.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            HealthMetricsHistoryResponse with paginated metrics
            
        Raises:
            HTTPException: If user not found or invalid pagination params
        """
        # Validate pagination parameters
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page must be greater than 0"
            )
        
        if page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page size must be between 1 and 100"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get total count
        total_count = (
            db.query(HealthMetrics)
            .filter(HealthMetrics.user_id == user_id)
            .count()
        )
        
        # Calculate pagination
        total_pages = ceil(total_count / page_size) if total_count > 0 else 1
        offset = (page - 1) * page_size
        
        # Get paginated health metrics with predictions
        metrics_query = (
            db.query(HealthMetrics)
            .filter(HealthMetrics.user_id == user_id)
            .order_by(desc(HealthMetrics.recorded_at))
            .offset(offset)
            .limit(page_size)
        )
        
        metrics_list = metrics_query.all()
        
        # Build history items with predictions
        history_items = []
        for metric in metrics_list:
            # Get associated prediction if available
            prediction = (
                db.query(Prediction)
                .filter(Prediction.metric_id == metric.metric_id)
                .first()
            )
            
            prediction_data = None
            if prediction:
                prediction_data = {
                    "prediction_id": str(prediction.prediction_id),
                    "classification": prediction.classification,
                    "confidence": float(prediction.confidence)
                }
            
            history_item = HealthMetricsHistoryItem(
                metric_id=str(metric.metric_id),
                weight_kg=float(metric.weight_kg),
                blood_sugar_mgdl=float(metric.blood_sugar_mgdl),
                age=metric.age,
                height_cm=float(metric.height_cm),
                bmi=float(metric.bmi) if metric.bmi else 0.0,
                symptoms=metric.symptoms if metric.symptoms else None,
                recorded_at=metric.recorded_at,
                prediction=prediction_data
            )
            history_items.append(history_item)
        
        return HealthMetricsHistoryResponse(
            metrics=history_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
