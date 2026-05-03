"""
Prediction model for storing ML model predictions.
"""

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, CheckConstraint, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import UUID, JSONB


class Prediction(Base):
    """Prediction model for ML model results."""
    
    __tablename__ = "predictions"
    
    prediction_id = Column(
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
    metric_id = Column(
        UUID(), 
        ForeignKey("health_metrics.metric_id", ondelete="CASCADE"), 
        nullable=False
    )
    model_version = Column(String(50), nullable=False)
    classification = Column(String(50), nullable=False)
    confidence = Column(Numeric(5, 4), nullable=False)
    probabilities = Column(JSONB, nullable=False)
    predicted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "classification IN ('Type 1', 'Type 2', 'No Diabetes', 'Has Diabetes')", 
            name='classification_values'
        ),
        CheckConstraint('confidence BETWEEN 0 AND 1', name='confidence_range'),
    )
    
    # Relationships
    user = relationship("User", back_populates="predictions")
    health_metric = relationship("HealthMetrics", back_populates="predictions")