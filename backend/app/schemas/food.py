"""
Pydantic schemas for food API endpoints.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal


class NutrientInfo(BaseModel):
    """Nutrient information in food response."""
    
    nutrient_id: UUID
    name: str
    amount: Decimal
    unit: str
    per_unit: str = "100g"
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "nutrient_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Protein",
                "amount": "7.5",
                "unit": "G",
                "per_unit": "100g"
            }
        }


class FoodSearchResult(BaseModel):
    """Food search result item."""
    
    food_id: UUID
    name: str
    category: str
    food_type: Optional[str] = None
    allergens: Optional[List[str]] = None
    calories_per_serving: Optional[float] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "food_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Hummus",
                "category": "Legumes and Legume Products",
                "food_type": "sample_food",
                "allergens": ["Sesame"],
                "calories_per_serving": 166.0
            }
        }


class FoodDetail(BaseModel):
    """Detailed food information."""
    
    food_id: UUID
    name: str
    description: Optional[str] = None
    category: str
    food_type: Optional[str] = None
    allergens: Optional[List[str]] = None
    nutrients: List[NutrientInfo] = Field(default_factory=list)
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "food_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Hummus",
                "description": "HUMMUS, SABRA CLASSIC",
                "category": "Legumes and Legume Products",
                "food_type": "sample_food",
                "allergens": ["Sesame"],
                "nutrients": [],
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class FoodSearchRequest(BaseModel):
    """Food search request parameters."""
    
    query: Optional[str] = Field(None, description="Search query text")
    category: Optional[str] = Field(None, description="Filter by category")
    allergens: Optional[List[str]] = Field(
        None, 
        description="Exclude foods with these allergens"
    )
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "chicken",
                "category": "Poultry Products",
                "allergens": ["Dairy"],
                "page": 1,
                "page_size": 20
            }
        }


class FoodSearchResponse(BaseModel):
    """Food search response with pagination."""
    
    foods: List[FoodSearchResult]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "foods": [],
                "total": 150,
                "page": 1,
                "page_size": 20,
                "total_pages": 8
            }
        }


class ServingSize(BaseModel):
    """Common serving size information."""
    
    unit: str
    amount: Decimal
    description: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "unit": "cup",
                "amount": "1.0",
                "description": "1 cup"
            }
        }


class FoodServingSizes(BaseModel):
    """Common serving sizes for a food."""
    
    food_id: UUID
    serving_sizes: List[ServingSize]
    
    class Config:
        json_schema_extra = {
            "example": {
                "food_id": "123e4567-e89b-12d3-a456-426614174000",
                "serving_sizes": [
                    {"unit": "cup", "amount": "1.0", "description": "1 cup"},
                    {"unit": "tbsp", "amount": "2.0", "description": "2 tablespoons"}
                ]
            }
        }


class CustomFoodCreate(BaseModel):
    """Schema for creating a custom food entry."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Food name")
    serving_size: str = Field(..., description="Serving size description (e.g., '1 cup', '100g')")
    calories: Decimal = Field(..., ge=0, description="Calories per serving")
    carbohydrates_g: Optional[Decimal] = Field(None, ge=0, description="Carbohydrates in grams")
    protein_g: Optional[Decimal] = Field(None, ge=0, description="Protein in grams")
    fat_g: Optional[Decimal] = Field(None, ge=0, description="Fat in grams")
    fiber_g: Optional[Decimal] = Field(None, ge=0, description="Fiber in grams")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Homemade Chicken Salad",
                "serving_size": "1 bowl",
                "calories": "350",
                "carbohydrates_g": "15",
                "protein_g": "30",
                "fat_g": "18",
                "fiber_g": "3"
            }
        }
