"""
Nutrient model for nutritional information.
"""

from sqlalchemy import Column, String, CheckConstraint, text
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import UUID


class Nutrient(Base):
    """Nutrient model for nutritional information."""
    
    __tablename__ = "nutrients"
    
    nutrient_id = Column(
        UUID(), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    name = Column(String(255), nullable=False, unique=True)
    unit = Column(String(20), nullable=False)
    nutrient_type = Column(String(50), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "nutrient_type IN ('macronutrient', 'vitamin', 'mineral', 'other')", 
            name='nutrient_type_values'
        ),
    )
    
    # Relationships
    food_nutrients = relationship("FoodNutrient", back_populates="nutrient", cascade="all, delete-orphan")