"""
Comprehensive error handling middleware.
Provides structured error responses and logging.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import traceback
import logging
import uuid
from typing import Optional

from app.core.config import settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling errors and providing structured responses.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Process request with error handling."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            # Log the error with context
            user_id = getattr(request.state, 'user_id', 'anonymous')
            
            error_context = {
                "request_id": request_id,
                "user_id": user_id,
                "method": request.method,
                "url": str(request.url),
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            
            # Log with stack trace
            logger.error(
                f"Request failed: {error_context}",
                exc_info=True
            )
            
            # Determine error response
            status_code, error_code, user_message = self._categorize_error(exc)
            
            # Build error response
            error_response = {
                "error": {
                    "code": error_code,
                    "message": user_message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "requestId": request_id,
                }
            }
            
            # Include details in development mode
            if settings.DEBUG if hasattr(settings, 'DEBUG') else False:
                error_response["error"]["details"] = str(exc)
                error_response["error"]["traceback"] = traceback.format_exc()
            
            return JSONResponse(
                status_code=status_code,
                content=error_response,
                headers={"X-Request-ID": request_id}
            )
    
    def _categorize_error(self, exc: Exception) -> tuple:
        """
        Categorize exception and return appropriate response details.
        
        Returns:
            Tuple of (status_code, error_code, user_message)
        """
        error_type = type(exc).__name__
        
        # Database errors
        if "Database" in error_type or "SQL" in error_type:
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "SERVER_DATABASE_ERROR",
                "A database error occurred. Please try again later."
            )
        
        # Validation errors
        if "Validation" in error_type or "Pydantic" in error_type:
            return (
                status.HTTP_400_BAD_REQUEST,
                "VALIDATION_INVALID_INPUT",
                "Invalid input data. Please check your request."
            )
        
        # Authentication errors
        if "Auth" in error_type or "Unauthorized" in error_type:
            return (
                status.HTTP_401_UNAUTHORIZED,
                "AUTH_INVALID_CREDENTIALS",
                "Authentication failed. Please check your credentials."
            )
        
        # Not found errors
        if "NotFound" in error_type or "404" in str(exc):
            return (
                status.HTTP_404_NOT_FOUND,
                "RESOURCE_NOT_FOUND",
                "The requested resource was not found."
            )
        
        # Default to internal server error
        return (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "SERVER_INTERNAL_ERROR",
            "An unexpected error occurred. Please try again later."
        )
