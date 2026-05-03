"""
Food model for food database.
"""

from sqlalchemy import Column, String, Text, DateTime, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import UUID, ARRAY


class Food(Base):
    """Food model for food database."""
    
    __tablename__ = "foods"
    
    food_id = Column(
        UUID(), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    food_type = Column(String(100), nullable=True)
    allergens = Column(ARRAY(Text), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    food_nutrients = relationship("FoodNutrient", back_populates="food", cascade="all, delete-orphan")
    food_entries = relationship("FoodEntry", back_populates="food")