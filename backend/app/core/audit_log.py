"""
Audit logging service for HIPAA compliance.
Logs all data access and modifications with context.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import json
import os
from pathlib import Path


class AuditAction(str, Enum):
    """Audit action types."""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    FAILED_LOGIN = "FAILED_LOGIN"
    PREDICTION = "PREDICTION"
    DATA_EXPORT = "DATA_EXPORT"
    DATA_DELETION = "DATA_DELETION"


class AuditResourceType(str, Enum):
    """Resource types for audit logging."""
    USER = "USER"
    HEALTH_METRICS = "HEALTH_METRICS"
    PREDICTION = "PREDICTION"
    FOOD_ENTRY = "FOOD_ENTRY"
    USER_PROFILE = "USER_PROFILE"
    AUTHENTICATION = "AUTHENTICATION"


# Ensure logs directory exists
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Create file handler for audit logs
audit_handler = logging.FileHandler("logs/audit.log")
audit_handler.setLevel(logging.INFO)

# Create formatter
audit_formatter = logging.Formatter(
    '%(asctime)s - AUDIT - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)


class AuditLogger:
    """Service for audit logging."""
    
    @staticmethod
    def log(
        action: AuditAction,
        resource_type: AuditResourceType,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        Log an audit event.
        
        Args:
            action: The action performed
            resource_type: Type of resource accessed
            resource_id: ID of the specific resource
            user_id: ID of the user performing the action
            request_id: Request ID for tracing
            ip_address: IP address of the client
            details: Additional details about the action
            success: Whether the action succeeded
            error_message: Error message if action failed
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action.value,
            "resource_type": resource_type.value,
            "resource_id": resource_id,
            "user_id": user_id,
            "request_id": request_id,
            "ip_address": ip_address,
            "success": success,
            "error_message": error_message,
            "details": details or {}
        }
        
        # Log as JSON for easy parsing
        audit_logger.info(json.dumps(audit_entry))
    
    @staticmethod
    def log_data_access(
        user_id: str,
        resource_type: AuditResourceType,
        resource_id: str,
        action: AuditAction,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """
        Log health data access (READ, UPDATE, DELETE).
        
        Args:
            user_id: ID of the user accessing data
            resource_type: Type of resource
            resource_id: ID of the resource
            action: Action performed
            request_id: Request ID for tracing
            ip_address: IP address of the client
        """
        AuditLogger.log(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            request_id=request_id,
            ip_address=ip_address,
            details={"data_type": "PHI"}  # Protected Health Information
        )
    
    @staticmethod
    def log_authentication(
        user_id: Optional[str],
        action: AuditAction,
        success: bool,
        ip_address: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """
        Log authentication events.
        
        Args:
            user_id: ID of the user (if known)
            action: LOGIN, LOGOUT, or FAILED_LOGIN
            success: Whether authentication succeeded
            ip_address: IP address of the client
            error_message: Error message if failed
        """
        AuditLogger.log(
            action=action,
            resource_type=AuditResourceType.AUTHENTICATION,
            user_id=user_id,
            ip_address=ip_address,
            success=success,
            error_message=error_message
        )
    
    @staticmethod
    def log_prediction(
        user_id: str,
        prediction_id: str,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log ML prediction generation.
        
        Args:
            user_id: ID of the user
            prediction_id: ID of the prediction
            request_id: Request ID for tracing
            details: Additional prediction details
        """
        AuditLogger.log(
            action=AuditAction.PREDICTION,
            resource_type=AuditResourceType.PREDICTION,
            resource_id=prediction_id,
            user_id=user_id,
            request_id=request_id,
            details=details
        )
    
    @staticmethod
    def log_data_deletion(
        user_id: str,
        resource_type: AuditResourceType,
        resource_id: str,
        request_id: Optional[str] = None,
        permanent: bool = False
    ):
        """
        Log data deletion events.
        
        Args:
            user_id: ID of the user
            resource_type: Type of resource deleted
            resource_id: ID of the resource
            request_id: Request ID for tracing
            permanent: Whether deletion is permanent
        """
        AuditLogger.log(
            action=AuditAction.DATA_DELETION,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            request_id=request_id,
            details={"permanent": permanent}
        )


# Global audit logger instance
audit_log = AuditLogger()
