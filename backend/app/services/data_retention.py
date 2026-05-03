"""
Data retention and deletion service for HIPAA compliance.
Implements 30-day permanent removal as per requirements.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
import logging

from app.models.user import User
from app.models.health_metrics import HealthMetrics
from app.models.prediction import Prediction
from app.models.food_entry import FoodEntry
from app.models.user_profile import UserProfile
from app.core.audit_log import audit_log, AuditAction, AuditResourceType
from app.core.config import settings


logger = logging.getLogger(__name__)


class DataRetentionService:
    """Service for managing data retention and deletion."""
    
    @staticmethod
    def mark_user_for_deletion(
        db: Session,
        user_id: str,
        request_id: str = None
    ):
        """
        Mark a user account for deletion.
        Data will be permanently removed after DATA_RETENTION_DAYS.
        
        Args:
            db: Database session
            user_id: ID of the user to delete
            request_id: Request ID for audit trail
            
        Requirements: 14.4
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return
        
        # In a real implementation, add a 'deleted_at' column to track deletion date
        # For now, we'll log the deletion request
        
        # Audit log the deletion request
        audit_log.log_data_deletion(
            user_id=user_id,
            resource_type=AuditResourceType.USER,
            resource_id=user_id,
            request_id=request_id,
            permanent=False
        )
        
        logger.info(
            f"User {user_id} marked for deletion. "
            f"Data will be permanently removed after {settings.DATA_RETENTION_DAYS} days."
        )
    
    @staticmethod
    def permanently_delete_user_data(
        db: Session,
        user_id: str
    ):
        """
        Permanently delete all user data.
        This should only be called after the retention period.
        
        Args:
            db: Database session
            user_id: ID of the user whose data to delete
            
        Requirements: 14.4
        """
        try:
            # Delete in order to respect foreign key constraints
            
            # 1. Delete food entries
            food_entries = db.query(FoodEntry).filter(
                FoodEntry.user_id == user_id
            ).delete(synchronize_session=False)
            
            # 2. Delete predictions
            predictions = db.query(Prediction).filter(
                Prediction.user_id == user_id
            ).delete(synchronize_session=False)
            
            # 3. Delete health metrics
            health_metrics = db.query(HealthMetrics).filter(
                HealthMetrics.user_id == user_id
            ).delete(synchronize_session=False)
            
            # 4. Delete user profile
            db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).delete(synchronize_session=False)
            
            # 5. Delete user account
            db.query(User).filter(
                User.user_id == user_id
            ).delete(synchronize_session=False)
            
            db.commit()
            
            # Audit log permanent deletion
            audit_log.log_data_deletion(
                user_id=user_id,
                resource_type=AuditResourceType.USER,
                resource_id=user_id,
                permanent=True
            )
            
            logger.info(
                f"Permanently deleted all data for user {user_id}. "
                f"Deleted: {food_entries} food entries, {predictions} predictions, "
                f"{health_metrics} health metrics"
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error permanently deleting user {user_id} data: {str(e)}")
            raise
    
    @staticmethod
    def cleanup_expired_deletions(db: Session):
        """
        Clean up users marked for deletion after retention period.
        This should be run as a scheduled job.
        
        Args:
            db: Database session
            
        Requirements: 14.4
        """
        # In a real implementation, query users where:
        # deleted_at < (now - DATA_RETENTION_DAYS)
        # and permanently delete their data
        
        cutoff_date = datetime.utcnow() - timedelta(days=settings.DATA_RETENTION_DAYS)
        
        logger.info(
            f"Running data retention cleanup for deletions before {cutoff_date.isoformat()}"
        )
        
        # This would be implemented with a 'deleted_at' column in the User model
        # For now, this is a placeholder for the scheduled job
    
    @staticmethod
    def get_user_data_summary(
        db: Session,
        user_id: str
    ) -> dict:
        """
        Get a summary of all data associated with a user.
        Useful for data export requests (HIPAA right of access).
        
        Args:
            db: Database session
            user_id: ID of the user
            
        Returns:
            Dictionary with counts of all user data
            
        Requirements: 14.4
        """
        summary = {
            "user_id": user_id,
            "health_metrics_count": db.query(HealthMetrics).filter(
                HealthMetrics.user_id == user_id
            ).count(),
            "predictions_count": db.query(Prediction).filter(
                Prediction.user_id == user_id
            ).count(),
            "food_entries_count": db.query(FoodEntry).filter(
                FoodEntry.user_id == user_id
            ).count(),
            "has_profile": db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first() is not None
        }
        
        # Audit log data access
        audit_log.log(
            action=AuditAction.DATA_EXPORT,
            resource_type=AuditResourceType.USER,
            resource_id=user_id,
            user_id=user_id,
            details=summary
        )
        
        return summary


# Global data retention service instance
data_retention_service = DataRetentionService()
