"""
Security utilities for authentication and encryption.
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status

from app.core.config import settings


def create_access_token(
    subject: Union[str, int], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> str:
    """Verify JWT token and return subject."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # Truncate password to 72 bytes for bcrypt compatibility
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """Generate password hash with bcrypt (12 rounds as per requirements)."""
    # Truncate password to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')[:72]
    # Use 12 rounds as specified in requirements
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')