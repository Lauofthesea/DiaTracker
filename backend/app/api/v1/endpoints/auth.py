"""
Authentication endpoints for user registration, login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.schemas.auth import (
    UserRegistration,
    UserLogin,
    TokenResponse,
    TokenRefreshResponse,
    UserResponse
)
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.audit_log import audit_log, AuditAction, AuditResourceType
from app.core.sanitization import input_sanitizer


router = APIRouter()


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "unknown"


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserRegistration,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    **Requirements:** 1.1, 1.4, 14.1, 14.2, 14.3
    
    **Request Body:**
    - name: User's full name (required)
    - email: Valid email address (required)
    - password: Password meeting strength requirements (required)
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
    
    **Response:**
    - access_token: JWT token for authentication
    - token_type: "bearer"
    - expires_in: Token expiration time in seconds (86400 = 24 hours)
    - user_id: Unique user identifier
    - is_first_login: True for new registrations
    
    **Errors:**
    - 400: Email already registered or validation failed
    - 500: Server error during registration
    
    **Security:**
    - Input sanitization to prevent XSS
    - Password hashing with bcrypt (12 rounds)
    - Audit logging for compliance
    """
    # Sanitize inputs
    if not input_sanitizer.validate_safe_input(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input detected"
        )
    
    if not input_sanitizer.validate_safe_input(user_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input detected"
        )
    
    # Sanitize name
    user_data.name = input_sanitizer.sanitize_string(user_data.name, max_length=255)
    
    try:
        response = AuthService.register_user(db, user_data)
        
        # Audit log successful registration
        audit_log.log_authentication(
            user_id=response.user_id,
            action=AuditAction.CREATE,
            success=True,
            ip_address=get_client_ip(request)
        )
        
        return response
    except Exception as e:
        # Audit log failed registration
        audit_log.log_authentication(
            user_id=None,
            action=AuditAction.CREATE,
            success=False,
            ip_address=get_client_ip(request),
            error_message=str(e)
        )
        raise


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and generate access token.
    
    **Requirements:** 1.2, 1.5, 14.1, 14.2, 14.3, 17.5
    
    **Request Body:**
    - email: User's email address (required)
    - password: User's password (required)
    
    **Response:**
    - access_token: JWT token for authentication
    - token_type: "bearer"
    - expires_in: Token expiration time in seconds (86400 = 24 hours)
    - user_id: Unique user identifier
    - is_first_login: Whether user has completed first login flow
    
    **Errors:**
    - 401: Invalid email or password
    
    **Security:**
    - Input sanitization
    - Audit logging for all authentication attempts
    - Rate limiting (100 requests/minute)
    
    **Note:** Session expires after 24 hours of inactivity (Requirement 1.5)
    """
    # Sanitize email input
    if not input_sanitizer.validate_safe_input(login_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input detected"
        )
    
    try:
        response = AuthService.login_user(db, login_data)
        
        # Audit log successful login
        audit_log.log_authentication(
            user_id=response.user_id,
            action=AuditAction.LOGIN,
            success=True,
            ip_address=get_client_ip(request)
        )
        
        return response
    except HTTPException as e:
        # Audit log failed login
        audit_log.log_authentication(
            user_id=None,
            action=AuditAction.FAILED_LOGIN,
            success=False,
            ip_address=get_client_ip(request),
            error_message=f"Failed login attempt for {login_data.email}"
        )
        raise


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Refresh access token for authenticated user.
    
    **Requirements:** 1.5
    
    **Headers:**
    - Authorization: Bearer <access_token>
    
    **Response:**
    - access_token: New JWT token
    - token_type: "bearer"
    - expires_in: Token expiration time in seconds (86400 = 24 hours)
    
    **Errors:**
    - 401: Invalid or expired token
    - 404: User not found
    
    **Note:** This endpoint implements token rotation for security
    """
    token_response = AuthService.refresh_token(db, str(current_user.user_id))
    
    return TokenRefreshResponse(
        access_token=token_response.access_token,
        token_type=token_response.token_type,
        expires_in=token_response.expires_in
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user.
    
    **Requirements:** 17.5
    
    **Headers:**
    - Authorization: Bearer <access_token>
    
    **Response:**
    - success: True
    
    **Security:**
    - Audit logging for logout events
    
    **Note:** Client should discard the token after logout.
    Token will expire naturally after 24 hours.
    """
    # Audit log logout
    audit_log.log_authentication(
        user_id=str(current_user.user_id),
        action=AuditAction.LOGOUT,
        success=True,
        ip_address=get_client_ip(request)
    )
    
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    **Headers:**
    - Authorization: Bearer <access_token>
    
    **Response:**
    - user_id: Unique user identifier
    - email: User's email address
    - name: User's full name
    - created_at: Account creation timestamp
    - last_login: Last login timestamp
    - first_login_completed: Whether user completed first login flow
    
    **Errors:**
    - 401: Invalid or expired token
    """
    return UserResponse(
        user_id=str(current_user.user_id),
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        first_login_completed=current_user.first_login_completed
    )
