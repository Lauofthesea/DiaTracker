"""
Prediction log model for ML performance monitoring.
"""

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import UUID, JSONB


class PredictionLog(Base):
    """Detailed prediction log for performance monitoring."""
    
    __tablename__ = "prediction_logs"
    
    log_id = Column(UUID(), primary_key=True, server_default=func.gen_random_uuid())
    prediction_id = Column(UUID(), ForeignKey("predictions.prediction_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    model_version = Column(String(50), nullable=False, index=True)
    input_features = Column(JSONB, nullable=False)
    predicted_class = Column(String(50), nullable=False)
    confidence = Column(Numeric(5, 4), nullable=False)
    probabilities = Column(JSONB, nullable=False)
    ground_truth = Column(String(50), nullable=True)  # Actual diagnosis (if available)
    is_correct = Column(Boolean, nullable=True)  # Whether prediction matched ground truth
    logged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    prediction = relationship("Prediction", backref="logs")
    user = relationship("User", backref="prediction_logs")


class ModelPerformanceMetrics(Base):
    """Aggregated model performance metrics."""
    
    __tablename__ = "model_performance_metrics"
    
    metric_id = Column(UUID(), primary_key=True, server_default=func.gen_random_uuid())
    model_version = Column(String(50), nullable=False, index=True)
    window_size = Column(Integer, nullable=False)  # Number of predictions in window
    accuracy = Column(Numeric(5, 4), nullable=True)
    precision_type1 = Column(Numeric(5, 4), nullable=True)
    precision_type2 = Column(Numeric(5, 4), nullable=True)
    precision_no_diabetes = Column(Numeric(5, 4), nullable=True)
    recall_type1 = Column(Numeric(5, 4), nullable=True)
    recall_type2 = Column(Numeric(5, 4), nullable=True)
    recall_no_diabetes = Column(Numeric(5, 4), nullable=True)
    f1_type1 = Column(Numeric(5, 4), nullable=True)
    f1_type2 = Column(Numeric(5, 4), nullable=True)
    f1_no_diabetes = Column(Numeric(5, 4), nullable=True)
    confusion_matrix = Column(JSONB, nullable=True)
    total_predictions = Column(Integer, nullable=False)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class ModelPerformanceAlert(Base):
    """Model performance alerts."""
    
    __tablename__ = "model_performance_alerts"
    
    alert_id = Column(UUID(), primary_key=True, server_default=func.gen_random_uuid())
    model_version = Column(String(50), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(String, nullable=False)
    metric_value = Column(Numeric(10, 4), nullable=True)
    threshold_value = Column(Numeric(10, 4), nullable=True)
    is_resolved = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
