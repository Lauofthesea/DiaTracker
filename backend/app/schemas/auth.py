"""
Authentication schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class UserRegistration(BaseModel):
    """Schema for user registration request."""
    
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="User's password")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets strength requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class UserLogin(BaseModel):
    """Schema for user login request."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_id: str = Field(..., description="User's unique identifier")
    is_first_login: bool = Field(default=False, description="Whether this is the user's first login")


class TokenRefreshResponse(BaseModel):
    """Schema for token refresh response."""
    
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class UserResponse(BaseModel):
    """Schema for user information response."""
    
    user_id: str
    email: str
    name: str
    created_at: datetime
    last_login: Optional[datetime] = None
    first_login_completed: bool
    
    class Config:
        from_attributes = True
