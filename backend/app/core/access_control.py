"""
Data access control for HIPAA compliance.
Ensures users can only access their own data.
"""

from fastapi import HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session

from app.core.audit_log import audit_log, AuditAction, AuditResourceType


class AccessControl:
    """Service for enforcing data access restrictions."""
    
    @staticmethod
    def verify_user_access(
        current_user_id: str,
        resource_user_id: str,
        resource_type: AuditResourceType,
        resource_id: Optional[str] = None,
        action: AuditAction = AuditAction.READ
    ):
        """
        Verify that the current user has access to the resource.
        Users can only access their own data (HIPAA requirement 14.3).
        
        Args:
            current_user_id: ID of the authenticated user
            resource_user_id: ID of the user who owns the resource
            resource_type: Type of resource being accessed
            resource_id: ID of the specific resource
            action: Action being performed
            
        Raises:
            HTTPException: If access is denied
        """
        if current_user_id != resource_user_id:
            # Log unauthorized access attempt
            audit_log.log(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                user_id=current_user_id,
                success=False,
                error_message=f"Unauthorized access attempt to user {resource_user_id}'s data"
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )
        
        # Log successful access
        audit_log.log_data_access(
            user_id=current_user_id,
            resource_type=resource_type,
            resource_id=resource_id or "unknown",
            action=action
        )
    
    @staticmethod
    def verify_health_data_access(
        db: Session,
        current_user_id: str,
        metric_id: str
    ):
        """
        Verify access to health metrics data.
        
        Args:
            db: Database session
            current_user_id: ID of the authenticated user
            metric_id: ID of the health metric
            
        Raises:
            HTTPException: If access is denied or resource not found
        """
        from app.models.health_metrics import HealthMetrics
        
        metric = db.query(HealthMetrics).filter(
            HealthMetrics.metric_id == metric_id
        ).first()
        
        if not metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health metric not found"
            )
        
        AccessControl.verify_user_access(
            current_user_id=current_user_id,
            resource_user_id=str(metric.user_id),
            resource_type=AuditResourceType.HEALTH_METRICS,
            resource_id=metric_id,
            action=AuditAction.READ
        )
    
    @staticmethod
    def verify_prediction_access(
        db: Session,
        current_user_id: str,
        prediction_id: str
    ):
        """
        Verify access to prediction data.
        
        Args:
            db: Database session
            current_user_id: ID of the authenticated user
            prediction_id: ID of the prediction
            
        Raises:
            HTTPException: If access is denied or resource not found
        """
        from app.models.prediction import Prediction
        
        prediction = db.query(Prediction).filter(
            Prediction.prediction_id == prediction_id
        ).first()
        
        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prediction not found"
            )
        
        AccessControl.verify_user_access(
            current_user_id=current_user_id,
            resource_user_id=str(prediction.user_id),
            resource_type=AuditResourceType.PREDICTION,
            resource_id=prediction_id,
            action=AuditAction.READ
        )
    
    @staticmethod
    def verify_food_entry_access(
        db: Session,
        current_user_id: str,
        entry_id: str,
        action: AuditAction = AuditAction.READ
    ):
        """
        Verify access to food entry data.
        
        Args:
            db: Database session
            current_user_id: ID of the authenticated user
            entry_id: ID of the food entry
            action: Action being performed (READ, UPDATE, DELETE)
            
        Raises:
            HTTPException: If access is denied or resource not found
        """
        from app.models.food_entry import FoodEntry
        
        entry = db.query(FoodEntry).filter(
            FoodEntry.entry_id == entry_id
        ).first()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food entry not found"
            )
        
        AccessControl.verify_user_access(
            current_user_id=current_user_id,
            resource_user_id=str(entry.user_id),
            resource_type=AuditResourceType.FOOD_ENTRY,
            resource_id=entry_id,
            action=action
        )


# Global access control instance
access_control = AccessControl()
