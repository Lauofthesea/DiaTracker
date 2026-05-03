"""
Authentication service for user registration and login.
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user import User
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
)
from app.core.config import settings
from app.schemas.auth import (
    UserRegistration,
    UserLogin,
    TokenResponse
)


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegistration) -> TokenResponse:
        """
        Register a new user.
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            TokenResponse with access token and user info
            
        Raises:
            HTTPException: If email already exists or registration fails
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = get_password_hash(user_data.password)
        
        # Create new user
        new_user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=password_hash,
            first_login_completed=False
        )
        
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
        
        # Generate access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(new_user.user_id),
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=str(new_user.user_id),
            is_first_login=True
        )
    
    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> TokenResponse:
        """
        Authenticate user and generate access token.
        
        Args:
            db: Database session
            login_data: User login credentials
            
        Returns:
            TokenResponse with access token and user info
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login timestamp
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user.user_id),
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=str(user.user_id),
            is_first_login=not user.first_login_completed
        )
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            
        Returns:
            User object or None if not found
        """
        return db.query(User).filter(User.user_id == user_id).first()
    
    @staticmethod
    def refresh_token(db: Session, user_id: str) -> TokenResponse:
        """
        Generate a new access token for an authenticated user.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            
        Returns:
            TokenResponse with new access token
            
        Raises:
            HTTPException: If user not found
        """
        user = AuthService.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user.user_id),
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=str(user.user_id),
            is_first_login=not user.first_login_completed
        )
