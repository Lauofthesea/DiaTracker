"""
Pydantic schemas for food entry API endpoints.
"""

from typing import Optional, Dict
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal


class FoodEntryCreate(BaseModel):
    """Schema for creating a new food entry."""
    
    food_id: UUID = Field(..., description="UUID of the food item")
    quantity: Decimal = Field(..., gt=0, description="Quantity consumed (must be positive)")
    unit: str = Field(..., min_length=1, max_length=20, description="Unit of measurement")
    meal_type: str = Field(..., description="Type of meal")
    consumed_at: datetime = Field(..., description="When the food was consumed")
    
    @field_validator('meal_type')
    @classmethod
    def validate_meal_type(cls, v: str) -> str:
        """Validate meal type is one of the allowed values."""
        allowed = ['breakfast', 'lunch', 'dinner', 'snack']
        if v.lower() not in allowed:
            raise ValueError(f"meal_type must be one of: {', '.join(allowed)}")
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "food_id": "123e4567-e89b-12d3-a456-426614174000",
                "quantity": "150.0",
                "unit": "g",
                "meal_type": "lunch",
                "consumed_at": "2024-01-15T12:30:00Z"
            }
        }


class FoodEntryUpdate(BaseModel):
    """Schema for updating an existing food entry."""
    
    quantity: Optional[Decimal] = Field(None, gt=0, description="Updated quantity")
    unit: Optional[str] = Field(None, min_length=1, max_length=20, description="Updated unit")
    meal_type: Optional[str] = Field(None, description="Updated meal type")
    
    @field_validator('meal_type')
    @classmethod
    def validate_meal_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate meal type is one of the allowed values."""
        if v is None:
            return v
        allowed = ['breakfast', 'lunch', 'dinner', 'snack']
        if v.lower() not in allowed:
            raise ValueError(f"meal_type must be one of: {', '.join(allowed)}")
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "quantity": "200.0",
                "unit": "g",
                "meal_type": "dinner"
            }
        }


class NutritionalTotals(BaseModel):
    """Nutritional totals for a food entry."""
    
    calories: float = Field(..., description="Total calories in kcal")
    protein_g: float = Field(..., description="Total protein in grams")
    carbohydrates_g: float = Field(..., description="Total carbohydrates in grams")
    fat_g: float = Field(..., description="Total fat in grams")
    fiber_g: float = Field(..., description="Total fiber in grams")
    vitamins: Dict[str, float] = Field(default_factory=dict, description="Vitamin amounts")
    minerals: Dict[str, float] = Field(default_factory=dict, description="Mineral amounts")
    
    class Config:
        json_schema_extra = {
            "example": {
                "calories": 250.5,
                "protein_g": 15.2,
                "carbohydrates_g": 30.1,
                "fat_g": 8.5,
                "fiber_g": 3.2,
                "vitamins": {"Vitamin C": 12.5},
                "minerals": {"Calcium": 150.0}
            }
        }


class FoodEntryResponse(BaseModel):
    """Schema for food entry response."""
    
    entry_id: UUID
    user_id: UUID
    food_id: UUID
    food_name: str = Field(..., description="Name of the food")
    quantity: Decimal
    unit: str
    meal_type: str
    consumed_at: datetime
    created_at: datetime
    nutritional_totals: NutritionalTotals
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "entry_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "food_id": "123e4567-e89b-12d3-a456-426614174002",
                "food_name": "Chicken Breast",
                "quantity": "150.0",
                "unit": "g",
                "meal_type": "lunch",
                "consumed_at": "2024-01-15T12:30:00Z",
                "created_at": "2024-01-15T12:35:00Z",
                "nutritional_totals": {
                    "calories": 247.5,
                    "protein_g": 46.5,
                    "carbohydrates_g": 0.0,
                    "fat_g": 5.4,
                    "fiber_g": 0.0,
                    "vitamins": {},
                    "minerals": {}
                }
            }
        }


class FoodEntryListResponse(BaseModel):
    """Schema for list of food entries with pagination."""
    
    entries: list[FoodEntryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "entries": [],
                "total": 45,
                "page": 1,
                "page_size": 20,
                "total_pages": 3
            }
        }


class DailyNutritionalSummary(BaseModel):
    """Daily nutritional summary for a specific date."""
    
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    total_calories: float
    total_protein_g: float
    total_carbohydrates_g: float
    total_fat_g: float
    total_fiber_g: float
    meal_breakdown: Dict[str, NutritionalTotals] = Field(
        default_factory=dict,
        description="Nutritional totals by meal type"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-15",
                "total_calories": 1850.5,
                "total_protein_g": 95.2,
                "total_carbohydrates_g": 210.5,
                "total_fat_g": 62.3,
                "total_fiber_g": 28.5,
                "meal_breakdown": {
                    "breakfast": {
                        "calories": 450.0,
                        "protein_g": 20.0,
                        "carbohydrates_g": 60.0,
                        "fat_g": 15.0,
                        "fiber_g": 8.0,
                        "vitamins": {},
                        "minerals": {}
                    }
                }
            }
        }
