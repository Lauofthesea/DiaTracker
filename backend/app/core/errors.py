"""
Structured error responses for consistent error handling.
Implements error format as per design document.
"""

from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class APIError(HTTPException):
    """Base class for API errors with structured response."""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """
        Initialize API error.
        
        Args:
            status_code: HTTP status code
            error_code: Application-specific error code
            message: User-friendly error message
            details: Technical details (only shown in dev mode)
            request_id: Request ID for tracing
        """
        self.error_code = error_code
        self.request_id = request_id or str(uuid.uuid4())
        
        error_response = {
            "error": {
                "code": error_code,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "requestId": self.request_id
            }
        }
        
        if details:
            error_response["error"]["details"] = details
        
        super().__init__(
            status_code=status_code,
            detail=error_response
        )


# Authentication Errors (401)
class InvalidCredentialsError(APIError):
    """Invalid email or password."""
    def __init__(self, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_INVALID_CREDENTIALS",
            message="Invalid email or password",
            request_id=request_id
        )


class TokenExpiredError(APIError):
    """JWT token has expired."""
    def __init__(self, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_TOKEN_EXPIRED",
            message="Your session has expired. Please log in again.",
            request_id=request_id
        )


class TokenInvalidError(APIError):
    """Malformed or invalid token."""
    def __init__(self, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_TOKEN_INVALID",
            message="Invalid authentication token",
            request_id=request_id
        )


# Authorization Errors (403)
class InsufficientPermissionsError(APIError):
    """User lacks required permissions."""
    def __init__(self, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTH_INSUFFICIENT_PERMISSIONS",
            message="You do not have permission to access this resource",
            request_id=request_id
        )


# Validation Errors (400)
class ValidationError(APIError):
    """Request body validation failed."""
    def __init__(self, details: str, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_INVALID_INPUT",
            message="Invalid input data",
            details=details,
            request_id=request_id
        )


class MissingFieldError(APIError):
    """Required field is missing."""
    def __init__(self, field_name: str, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_MISSING_FIELD",
            message=f"Required field '{field_name}' is missing",
            request_id=request_id
        )


class OutOfRangeError(APIError):
    """Value outside acceptable range."""
    def __init__(self, field_name: str, min_val: Any, max_val: Any, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_OUT_OF_RANGE",
            message=f"Value for '{field_name}' must be between {min_val} and {max_val}",
            request_id=request_id
        )


# Resource Errors (404)
class ResourceNotFoundError(APIError):
    """Requested resource does not exist."""
    def __init__(self, resource_type: str, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message=f"{resource_type} not found",
            request_id=request_id
        )


# Business Logic Errors (422)
class PredictionInsufficientDataError(APIError):
    """Missing required health metrics for prediction."""
    def __init__(self, missing_fields: list, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="PREDICTION_INSUFFICIENT_DATA",
            message="Cannot generate prediction: missing required health metrics",
            details=f"Missing fields: {', '.join(missing_fields)}",
            request_id=request_id
        )


class FoodEntryTooOldError(APIError):
    """Cannot edit entries older than 7 days."""
    def __init__(self, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="FOOD_ENTRY_TOO_OLD",
            message="Cannot edit food entries older than 7 days",
            request_id=request_id
        )


class ModelUnavailableError(APIError):
    """ML model service is unavailable."""
    def __init__(self, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="MODEL_UNAVAILABLE",
            message="Prediction service is temporarily unavailable. Please try again later.",
            request_id=request_id
        )


# Server Errors (500)
class InternalServerError(APIError):
    """Unexpected server error."""
    def __init__(self, details: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="SERVER_INTERNAL_ERROR",
            message="An unexpected error occurred. Please try again later.",
            details=details,
            request_id=request_id
        )


class DatabaseError(APIError):
    """Database connection or query error."""
    def __init__(self, details: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="SERVER_DATABASE_ERROR",
            message="A database error occurred. Please try again later.",
            details=details,
            request_id=request_id
        )


class MLServiceError(APIError):
    """ML model service error."""
    def __init__(self, details: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="SERVER_ML_SERVICE_ERROR",
            message="Machine learning service error. Please try again later.",
            details=details,
            request_id=request_id
        )
