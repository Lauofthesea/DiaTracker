"""
Prediction schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Dict, List
from datetime import datetime


class PredictionCreate(BaseModel):
    """Schema for creating a prediction request."""
    
    metric_id: str = Field(..., description="Health metrics ID to use for prediction")


class PredictionResponse(BaseModel):
    """Schema for prediction response."""
    
    prediction_id: str
    user_id: str
    metric_id: str
    model_version: str
    classification: str = Field(
        ..., 
        description="Diabetes classification: 'Type 1', 'Type 2', or 'No Diabetes'"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Confidence score between 0 and 1"
    )
    probabilities: Dict[str, float] = Field(
        ...,
        description="Probability distribution for each class"
    )
    predicted_at: datetime
    
    class Config:
        from_attributes = True


class PredictionHistory(BaseModel):
    """Schema for prediction history response."""
    
    predictions: List[PredictionResponse]
    total_count: int
    
    class Config:
        from_attributes = True


class PredictionWithMetrics(BaseModel):
    """Schema for prediction with associated health metrics."""
    
    prediction_id: str
    user_id: str
    classification: str
    confidence: float
    probabilities: Dict[str, float]
    predicted_at: datetime
    model_version: str
    health_metrics: Dict = Field(..., description="Associated health metrics data")
    
    class Config:
        from_attributes = True
