"""
ML model metadata for tracking model versions and performance.
"""

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, CheckConstraint, text, Index
from sqlalchemy.sql import func

from app.db.database import Base
from app.db.types import UUID, JSONB


class MLModelMetadata(Base):
    """ML model metadata for tracking model versions and performance."""
    
    __tablename__ = "ml_model_metadata"
    
    model_id = Column(
        UUID(), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)
    version = Column(String(50), nullable=False, unique=True)
    accuracy = Column(Numeric(5, 4), nullable=True)
    precision_type1 = Column(Numeric(5, 4), nullable=True)
    precision_type2 = Column(Numeric(5, 4), nullable=True)
    recall = Column(Numeric(5, 4), nullable=True)
    f1_score = Column(Numeric(5, 4), nullable=True)
    training_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    model_path = Column(String(500), nullable=False)
    feature_list = Column(JSONB, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "model_type IN ('Logistic Regression', 'Random Forest', 'Neural Network')", 
            name='model_type_values'
        ),
        Index('idx_ml_model_active', 'is_active', 'version'),
    )