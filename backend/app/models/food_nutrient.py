"""
Food-Nutrient junction model for nutritional data.
"""

from sqlalchemy import Column, String, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import UUID


class FoodNutrient(Base):
    """Food-Nutrient junction model for nutritional data."""
    
    __tablename__ = "food_nutrients"
    
    food_id = Column(
        UUID(), 
        ForeignKey("foods.food_id", ondelete="CASCADE"), 
        primary_key=True
    )
    nutrient_id = Column(
        UUID(), 
        ForeignKey("nutrients.nutrient_id", ondelete="CASCADE"), 
        primary_key=True
    )
    amount = Column(Numeric(10, 4), nullable=False)
    per_unit = Column(String(20), default='100g', nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_food_nutrients_food', 'food_id'),
    )
    
    # Relationships
    food = relationship("Food", back_populates="food_nutrients")
    nutrient = relationship("Nutrient", back_populates="food_nutrients")