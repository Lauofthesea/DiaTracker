"""
Health metrics model for storing user health data.
"""

from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, CheckConstraint, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, column_property

from app.db.database import Base
from app.db.types import UUID, JSONB


class HealthMetrics(Base):
    """Health metrics model for user health data."""
    
    __tablename__ = "health_metrics"
    
    metric_id = Column(
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
    weight_kg = Column(Numeric(5, 2), nullable=False)
    blood_sugar_mgdl = Column(Numeric(5, 2), nullable=False)
    age = Column(Integer, nullable=False)
    height_cm = Column(Numeric(5, 2), nullable=False)
    
    # BMI calculated as generated column (PostgreSQL only)
    # For SQLite, BMI will be calculated in application code
    bmi = Column(Numeric(4, 2), nullable=True)
    
    symptoms = Column(JSONB, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('weight_kg BETWEEN 20 AND 300', name='weight_range'),
        CheckConstraint('blood_sugar_mgdl BETWEEN 20 AND 600', name='blood_sugar_range'),
        CheckConstraint('age BETWEEN 1 AND 120', name='age_range'),
        CheckConstraint('height_cm BETWEEN 50 AND 250', name='height_range'),
    )
    
    # Relationships
    user = relationship("User", back_populates="health_metrics")
    predictions = relationship("Prediction", back_populates="health_metric", cascade="all, delete-orphan")