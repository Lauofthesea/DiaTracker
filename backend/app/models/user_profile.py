"""
User profile model for additional user information.
"""

from sqlalchemy import Column, DateTime, ForeignKey, text, Text, Integer, Numeric, String, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import UUID, ARRAY


class UserProfile(Base):
    """User profile model for additional user information."""
    
    __tablename__ = "user_profiles"
    
    user_id = Column(
        UUID(), 
        ForeignKey("users.user_id", ondelete="CASCADE"), 
        primary_key=True
    )
    age = Column(Integer, nullable=True)
    weight_kg = Column(Numeric(5, 2), nullable=True)
    height_cm = Column(Numeric(5, 2), nullable=True)
    gender = Column(String(20), nullable=True)  # 'Male', 'Female'
    is_pregnant = Column(Boolean, default=False, nullable=True)
    family_history = Column(Boolean, default=False, nullable=True)  # Family history of diabetes
    allergen_preferences = Column(ARRAY(Text), nullable=True)
    dietary_restrictions = Column(ARRAY(Text), nullable=True)
    health_conditions = Column(ARRAY(Text), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")