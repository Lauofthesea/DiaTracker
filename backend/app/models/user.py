"""
User model for authentication and user management.
"""

from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import UUID


class User(Base):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    user_id = Column(
        UUID(), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    first_login_completed = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    health_metrics = relationship("HealthMetrics", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    food_entries = relationship("FoodEntry", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")