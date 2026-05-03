"""
Food entry model for user meal tracking.
"""

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, CheckConstraint, text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import UUID


class FoodEntry(Base):
    """Food entry model for user meal tracking."""
    
    __tablename__ = "food_entries"
    
    entry_id = Column(
        UUID(), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    user_id = Column(
        UUID(), 
        ForeignKey("users.user_id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    food_id = Column(
        UUID(), 
        ForeignKey("foods.food_id", ondelete="RESTRICT"), 
        nullable=False
    )
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    meal_type = Column(String(20), nullable=False, index=True)
    consumed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')", 
            name='meal_type_values'
        ),
        CheckConstraint('quantity > 0', name='quantity_positive'),
        Index('idx_food_entries_user_date', 'user_id', 'consumed_at'),
    )
    
    # Relationships
    user = relationship("User", back_populates="food_entries")
    food = relationship("Food", back_populates="food_entries")