"""
Health metrics schemas for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class HealthMetricsCreate(BaseModel):
    """Schema for creating health metrics."""
    
    weight_kg: float = Field(
        ..., 
        ge=20.0, 
        le=300.0,
        description="Weight in kilograms (20-300 kg)"
    )
    blood_sugar_mgdl: float = Field(
        ..., 
        ge=20.0, 
        le=600.0,
        description="Blood sugar level in mg/dL (20-600 mg/dL)"
    )
    age: int = Field(
        ..., 
        ge=1, 
        le=120,
        description="Age in years (1-120 years)"
    )
    height_cm: float = Field(
        ..., 
        ge=50.0, 
        le=250.0,
        description="Height in centimeters (50-250 cm)"
    )
    symptoms: Optional[List[str]] = Field(
        default=None,
        description="List of symptoms (e.g., 'frequent_urination', 'excessive_thirst', 'fatigue', 'blurred_vision', 'slow_healing')"
    )
    
    @field_validator('weight_kg')
    @classmethod
    def validate_weight(cls, v: float) -> float:
        """Validate weight is within physiological range."""
        if not (20.0 <= v <= 300.0):
            raise ValueError('Weight must be between 20 and 300 kg')
        return round(v, 2)
    
    @field_validator('blood_sugar_mgdl')
    @classmethod
    def validate_blood_sugar(cls, v: float) -> float:
        """Validate blood sugar is within physiological range."""
        if not (20.0 <= v <= 600.0):
            raise ValueError('Blood sugar must be between 20 and 600 mg/dL')
        return round(v, 2)
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v: int) -> int:
        """Validate age is within reasonable range."""
        if not (1 <= v <= 120):
            raise ValueError('Age must be between 1 and 120 years')
        return v
    
    @field_validator('height_cm')
    @classmethod
    def validate_height(cls, v: float) -> float:
        """Validate height is within physiological range."""
        if not (50.0 <= v <= 250.0):
            raise ValueError('Height must be between 50 and 250 cm')
        return round(v, 2)
    
    @field_validator('symptoms')
    @classmethod
    def validate_symptoms(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate symptoms list contains valid symptom codes."""
        if v is None:
            return []
        
        valid_symptoms = {
            'frequent_urination',
            'excessive_thirst',
            'fatigue',
            'blurred_vision',
            'slow_healing',
            'unexplained_weight_loss',
            'increased_hunger',
            'tingling_hands_feet',
            'dry_skin',
            'frequent_infections'
        }
        
        for symptom in v:
            if symptom not in valid_symptoms:
                raise ValueError(f'Invalid symptom: {symptom}. Valid symptoms are: {", ".join(valid_symptoms)}')
        
        return v
    
    @computed_field
    @property
    def bmi(self) -> float:
        """Calculate BMI from weight and height."""
        height_m = self.height_cm / 100.0
        bmi_value = self.weight_kg / (height_m * height_m)
        return round(bmi_value, 2)


class HealthMetricsResponse(BaseModel):
    """Schema for health metrics response."""
    
    metric_id: str
    user_id: str
    weight_kg: float
    blood_sugar_mgdl: float
    age: int
    height_cm: float
    bmi: float
    symptoms: Optional[List[str]] = None
    recorded_at: datetime
    
    class Config:
        from_attributes = True


class HealthMetricsUpdate(BaseModel):
    """Schema for updating health metrics."""
    
    weight_kg: Optional[float] = Field(
        None, 
        ge=20.0, 
        le=300.0,
        description="Weight in kilograms (20-300 kg)"
    )
    blood_sugar_mgdl: Optional[float] = Field(
        None, 
        ge=20.0, 
        le=600.0,
        description="Blood sugar level in mg/dL (20-600 mg/dL)"
    )
    age: Optional[int] = Field(
        None, 
        ge=1, 
        le=120,
        description="Age in years (1-120 years)"
    )
    height_cm: Optional[float] = Field(
        None, 
        ge=50.0, 
        le=250.0,
        description="Height in centimeters (50-250 cm)"
    )
    symptoms: Optional[List[str]] = Field(
        None,
        description="List of symptoms"
    )
    
    @field_validator('weight_kg')
    @classmethod
    def validate_weight(cls, v: Optional[float]) -> Optional[float]:
        """Validate weight is within physiological range."""
        if v is not None and not (20.0 <= v <= 300.0):
            raise ValueError('Weight must be between 20 and 300 kg')
        return round(v, 2) if v is not None else None
    
    @field_validator('blood_sugar_mgdl')
    @classmethod
    def validate_blood_sugar(cls, v: Optional[float]) -> Optional[float]:
        """Validate blood sugar is within physiological range."""
        if v is not None and not (20.0 <= v <= 600.0):
            raise ValueError('Blood sugar must be between 20 and 600 mg/dL')
        return round(v, 2) if v is not None else None
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        """Validate age is within reasonable range."""
        if v is not None and not (1 <= v <= 120):
            raise ValueError('Age must be between 1 and 120 years')
        return v
    
    @field_validator('height_cm')
    @classmethod
    def validate_height(cls, v: Optional[float]) -> Optional[float]:
        """Validate height is within physiological range."""
        if v is not None and not (50.0 <= v <= 250.0):
            raise ValueError('Height must be between 50 and 250 cm')
        return round(v, 2) if v is not None else None


class HealthMetricsHistory(BaseModel):
    """Schema for health metrics history response."""
    
    metrics: List[HealthMetricsResponse]
    total_count: int
    
    class Config:
        from_attributes = True


class SymptomsEncoded(BaseModel):
    """Schema for encoded symptoms for ML model input."""
    
    frequent_urination: int = Field(default=0, ge=0, le=1)
    excessive_thirst: int = Field(default=0, ge=0, le=1)
    fatigue: int = Field(default=0, ge=0, le=1)
    blurred_vision: int = Field(default=0, ge=0, le=1)
    slow_healing: int = Field(default=0, ge=0, le=1)
    unexplained_weight_loss: int = Field(default=0, ge=0, le=1)
    increased_hunger: int = Field(default=0, ge=0, le=1)
    tingling_hands_feet: int = Field(default=0, ge=0, le=1)
    dry_skin: int = Field(default=0, ge=0, le=1)
    frequent_infections: int = Field(default=0, ge=0, le=1)
    
    @classmethod
    def from_symptoms_list(cls, symptoms: Optional[List[str]]) -> 'SymptomsEncoded':
        """Create encoded symptoms from list of symptom strings."""
        if symptoms is None:
            symptoms = []
        
        return cls(
            frequent_urination=1 if 'frequent_urination' in symptoms else 0,
            excessive_thirst=1 if 'excessive_thirst' in symptoms else 0,
            fatigue=1 if 'fatigue' in symptoms else 0,
            blurred_vision=1 if 'blurred_vision' in symptoms else 0,
            slow_healing=1 if 'slow_healing' in symptoms else 0,
            unexplained_weight_loss=1 if 'unexplained_weight_loss' in symptoms else 0,
            increased_hunger=1 if 'increased_hunger' in symptoms else 0,
            tingling_hands_feet=1 if 'tingling_hands_feet' in symptoms else 0,
            dry_skin=1 if 'dry_skin' in symptoms else 0,
            frequent_infections=1 if 'frequent_infections' in symptoms else 0
        )
