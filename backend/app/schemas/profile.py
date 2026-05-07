"""
User profile schemas for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class ProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="User's full name"
    )
    age: Optional[int] = Field(
        None,
        ge=1,
        le=120,
        description="User's age in years"
    )
    weight_kg: Optional[float] = Field(
        None,
        ge=20,
        le=300,
        description="User's weight in kilograms"
    )
    height_cm: Optional[float] = Field(
        None,
        ge=50,
        le=250,
        description="User's height in centimeters"
    )
    gender: Optional[str] = Field(
        None,
        description="User's gender (Male, Female)"
    )
    is_pregnant: Optional[bool] = Field(
        None,
        description="Whether the user is currently pregnant (only applicable for females)"
    )
    family_history: Optional[bool] = Field(
        None,
        description="Whether the user has a family history of diabetes"
    )
    allergen_preferences: Optional[List[str]] = Field(
        None,
        description="List of allergen preferences (e.g., ['Dairy', 'Nuts', 'Shellfish'])"
    )
    dietary_restrictions: Optional[List[str]] = Field(
        None,
        description="List of dietary restrictions (e.g., ['Vegetarian', 'Gluten-Free'])"
    )
    health_conditions: Optional[List[str]] = Field(
        None,
        description="List of health conditions (e.g., ['Type 2 Diabetes', 'Hypertension'])"
    )
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        """Validate gender is one of the allowed values."""
        if v is not None:
            allowed = ['Male', 'Female']
            if v not in allowed:
                raise ValueError(f'Gender must be one of: {", ".join(allowed)}')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate name is not empty after stripping whitespace."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Name cannot be empty')
        return v
    
    @field_validator('allergen_preferences', 'dietary_restrictions', 'health_conditions')
    @classmethod
    def validate_string_lists(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate string lists contain non-empty strings."""
        if v is not None:
            # Remove empty strings and strip whitespace
            cleaned = [item.strip() for item in v if item and item.strip()]
            return cleaned if cleaned else None
        return v


class CurrentHealthMetrics(BaseModel):
    """Schema for current health metrics in profile response."""
    
    weight_kg: float
    blood_sugar_mgdl: float
    age: int
    height_cm: float
    bmi: float
    recorded_at: datetime
    
    class Config:
        from_attributes = True


class ProfileResponse(BaseModel):
    """Schema for user profile response."""
    
    user_id: str
    name: str
    email: str
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    gender: Optional[str] = None
    is_pregnant: Optional[bool] = None
    family_history: Optional[bool] = None
    allergen_preferences: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    health_conditions: Optional[List[str]] = None
    current_health_metrics: Optional[CurrentHealthMetrics] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class HealthMetricsHistoryItem(BaseModel):
    """Schema for a single health metrics history item."""
    
    metric_id: str
    weight_kg: float
    blood_sugar_mgdl: float
    age: int
    height_cm: float
    bmi: float
    symptoms: Optional[List[str]] = None
    recorded_at: datetime
    prediction: Optional[dict] = None  # Contains prediction_id, classification, confidence if available
    
    class Config:
        from_attributes = True


class HealthMetricsHistoryResponse(BaseModel):
    """Schema for health metrics history response with pagination."""
    
    metrics: List[HealthMetricsHistoryItem]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True
