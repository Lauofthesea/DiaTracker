"""
Meal Risk Schemas - Request/response models for meal risk prediction API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime


class MealRiskRequest(BaseModel):
    """Request schema for meal risk prediction."""
    
    # Required meal composition
    available_carbs_g: float = Field(
        ...,
        ge=0,
        le=500,
        description="Available carbohydrates in meal (grams)"
    )
    fat_g: float = Field(
        ...,
        ge=0,
        le=200,
        description="Fat content in meal (grams)"
    )
    protein_g: float = Field(
        ...,
        ge=0,
        le=200,
        description="Protein content in meal (grams)"
    )
    fiber_g: float = Field(
        ...,
        ge=0,
        le=100,
        description="Fiber content in meal (grams)"
    )
    
    # Optional user context
    fasting_glucose: Optional[float] = Field(
        None,
        ge=50,
        le=400,
        description="Fasting glucose level (mg/dL). Defaults to 100 if not provided."
    )
    food_entry_id: Optional[str] = Field(
        None,
        description="Optional food entry ID to link prediction"
    )
    
    @field_validator('fasting_glucose')
    @classmethod
    def validate_glucose(cls, v):
        """Set default fasting glucose if not provided."""
        if v is None:
            return 100.0  # Default to normal fasting glucose
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "available_carbs_g": 45.0,
                "fat_g": 12.0,
                "protein_g": 25.0,
                "fiber_g": 8.0,
                "fasting_glucose": 105.0,
                "food_entry_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class MealRiskResponse(BaseModel):
    """Response schema for meal risk prediction."""
    
    prediction_id: Optional[str] = Field(None, description="Unique prediction ID (only set when meal is confirmed)")
    predicted_glucose_1hr: float = Field(
        ...,
        description="Predicted 1-hour post-meal glucose (mg/dL)"
    )
    confidence_interval: Dict[str, float] = Field(
        ...,
        description="95% confidence interval for prediction"
    )
    risk_level: str = Field(
        ...,
        description="Risk classification: Low, Mid, or High"
    )
    risk_explanation: str = Field(
        ...,
        description="Human-readable explanation of the risk"
    )
    model_version: str = Field(..., description="Model version used")
    predicted_at: str = Field(..., description="Prediction timestamp (ISO 8601)")
    warnings: List[str] = Field(
        default_factory=list,
        description="Optional warnings or notes"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction_id": "123e4567-e89b-12d3-a456-426614174000",
                "predicted_glucose_1hr": 145.2,
                "confidence_interval": {
                    "lower": 133.9,
                    "upper": 156.5
                },
                "risk_level": "Mid",
                "risk_explanation": "This meal may elevate your glucose to 145.2 mg/dL...",
                "model_version": "1.0.0-rf",
                "predicted_at": "2026-05-06T10:30:00Z",
                "warnings": []
            }
        }


class MealComposition(BaseModel):
    """Meal composition details."""
    
    available_carbs_g: float
    fat_g: float
    protein_g: float
    fiber_g: float


class MealPredictionHistoryItem(BaseModel):
    """Single item in meal prediction history."""
    
    prediction_id: str
    predicted_glucose_1hr: float
    risk_level: str
    meal_composition: MealComposition
    confidence_interval: Optional[Dict[str, Optional[float]]]
    predicted_at: str
    food_entry_id: Optional[str]


class PaginationInfo(BaseModel):
    """Pagination metadata."""
    
    page: int
    page_size: int
    total_count: int
    total_pages: int


class MealHistoryResponse(BaseModel):
    """Response schema for meal prediction history."""
    
    predictions: List[MealPredictionHistoryItem]
    pagination: PaginationInfo
    
    class Config:
        json_schema_extra = {
            "example": {
                "predictions": [
                    {
                        "prediction_id": "123e4567-e89b-12d3-a456-426614174000",
                        "predicted_glucose_1hr": 145.2,
                        "risk_level": "Mid",
                        "meal_composition": {
                            "available_carbs_g": 45.0,
                            "fat_g": 12.0,
                            "protein_g": 25.0,
                            "fiber_g": 8.0
                        },
                        "confidence_interval": {
                            "lower": 133.9,
                            "upper": 156.5
                        },
                        "predicted_at": "2026-05-06T10:30:00Z",
                        "food_entry_id": None
                    }
                ],
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total_count": 150,
                    "total_pages": 8
                }
            }
        }


class ModelInfoResponse(BaseModel):
    """Response schema for model information."""
    
    glucose_predictor: Dict
    risk_classifier: Dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "glucose_predictor": {
                    "version": "1.0.0-rf",
                    "loaded_at": "2026-05-06T10:00:00Z",
                    "features": ["fasting_glucose", "available_carbs_g", "fat_g", "protein_g", "fiber_g", "BMI", "age", "gender"],
                    "n_features": 8,
                    "status": "loaded"
                },
                "risk_classifier": {
                    "version": "2.0.0-rf",
                    "loaded_at": "2026-05-06T10:00:00Z",
                    "features": ["fasting_glucose", "BMI", "age", "gender"],
                    "n_features": 4,
                    "status": "loaded"
                }
            }
        }
