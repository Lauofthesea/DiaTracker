"""
Pydantic schemas for model performance monitoring.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class GroundTruthUpdate(BaseModel):
    """Schema for updating ground truth."""
    ground_truth: str = Field(..., description="Actual diagnosis")
    
    @validator('ground_truth')
    def validate_ground_truth(cls, v):
        valid_values = ['Type 1', 'Type 2', 'No Diabetes']
        if v not in valid_values:
            raise ValueError(f'ground_truth must be one of {valid_values}')
        return v


class AlertResponse(BaseModel):
    """Schema for performance alert response."""
    alert_id: str
    model_version: str
    alert_type: str
    severity: str
    message: str
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConfusionMatrixResponse(BaseModel):
    """Schema for confusion matrix response."""
    classes: List[str]
    matrix: List[List[int]]
    total: int


class ClassMetrics(BaseModel):
    """Schema for per-class metrics."""
    precision: float
    recall: float
    f1_score: float
    true_positives: int
    false_positives: int
    false_negatives: int


class PerformanceSummaryResponse(BaseModel):
    """Schema for comprehensive performance summary."""
    model_version: Optional[str]
    window_size: int
    accuracy: Optional[float]
    confusion_matrix: Optional[Dict[str, Any]]
    class_metrics: Optional[Dict[str, ClassMetrics]]
    active_alerts: List[Dict[str, Any]]
    should_retrain: bool
    retrain_reasons: List[str]
    total_predictions_with_ground_truth: int
    status: str


class RetrainingCheckResponse(BaseModel):
    """Schema for retraining check response."""
    should_retrain: bool
    reasons: List[str]
    model_version: Optional[str]
    recommendation: str


class PredictionLogResponse(BaseModel):
    """Schema for prediction log response."""
    log_id: str
    prediction_id: str
    user_id: str
    model_version: str
    input_features: Dict[str, Any]
    predicted_class: str
    confidence: float
    probabilities: Dict[str, float]
    ground_truth: Optional[str] = None
    is_correct: Optional[bool] = None
    logged_at: datetime
    
    class Config:
        from_attributes = True
