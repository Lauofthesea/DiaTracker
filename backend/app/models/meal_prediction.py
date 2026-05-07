"""
Meal Prediction Model - Stores meal-based glucose predictions.
"""

from sqlalchemy import Column, String, Integer, DECIMAL, TIMESTAMP, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class MealPrediction(Base):
    """Model for storing meal-based glucose predictions."""
    
    __tablename__ = "meal_predictions"
    
    # Primary key
    prediction_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    food_entry_id = Column(
        UUID(as_uuid=True),
        ForeignKey("food_entries.entry_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Input features
    fasting_glucose = Column(DECIMAL(5, 2), nullable=False)
    available_carbs_g = Column(DECIMAL(6, 2), nullable=False)
    fat_g = Column(DECIMAL(6, 2), nullable=False)
    protein_g = Column(DECIMAL(6, 2), nullable=False)
    fiber_g = Column(DECIMAL(6, 2), nullable=False)
    bmi = Column(DECIMAL(5, 2), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Integer, nullable=False)  # 0=Male, 1=Female
    
    # Prediction outputs
    predicted_glucose_1hr = Column(DECIMAL(6, 2), nullable=False)
    confidence_lower = Column(DECIMAL(6, 2), nullable=True)
    confidence_upper = Column(DECIMAL(6, 2), nullable=True)
    risk_level = Column(String(10), nullable=False)  # Low, Mid, High
    
    # Metadata
    model_version = Column(String(20), nullable=False)
    predicted_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_predictions', 'user_id', 'predicted_at'),
        Index('idx_risk_level', 'risk_level'),
        Index('idx_food_entry', 'food_entry_id'),
    )
    
    def __repr__(self):
        return (
            f"<MealPrediction(id={self.prediction_id}, "
            f"user_id={self.user_id}, "
            f"predicted_glucose={self.predicted_glucose_1hr}, "
            f"risk={self.risk_level})>"
        )
