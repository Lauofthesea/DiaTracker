"""
Pydantic schemas for analytics API endpoints.
"""

from typing import List, Dict, Optional
from datetime import date
from pydantic import BaseModel, Field


class MacronutrientDistribution(BaseModel):
    """Macronutrient distribution as percentages."""
    
    protein_percent: float = Field(..., description="Protein percentage of total calories")
    carbohydrates_percent: float = Field(..., description="Carbohydrates percentage of total calories")
    fat_percent: float = Field(..., description="Fat percentage of total calories")
    
    class Config:
        json_schema_extra = {
            "example": {
                "protein_percent": 25.5,
                "carbohydrates_percent": 50.2,
                "fat_percent": 24.3
            }
        }


class CarbohydrateWarning(BaseModel):
    """Warning about carbohydrate intake for diabetes management."""
    
    date: str = Field(..., description="Date of the warning (YYYY-MM-DD)")
    carbohydrates_g: float = Field(..., description="Total carbohydrates consumed in grams")
    recommended_max_g: float = Field(..., description="Recommended maximum carbohydrates in grams")
    severity: str = Field(..., description="Warning severity: 'moderate' or 'high'")
    message: str = Field(..., description="Warning message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-15",
                "carbohydrates_g": 280.5,
                "recommended_max_g": 225.0,
                "severity": "moderate",
                "message": "Carbohydrate intake is 24.7% above recommended level for diabetes management"
            }
        }


class PeriodSummaryResponse(BaseModel):
    """Summary of nutritional data for a time period."""
    
    period: str = Field(..., description="Period type: 'daily', 'weekly', or 'monthly'")
    start_date: str = Field(..., description="Start date of the period (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date of the period (YYYY-MM-DD)")
    total_calories: float = Field(..., description="Total calories consumed in the period")
    avg_daily_calories: float = Field(..., description="Average daily calories")
    total_protein_g: float = Field(..., description="Total protein in grams")
    total_carbohydrates_g: float = Field(..., description="Total carbohydrates in grams")
    total_fat_g: float = Field(..., description="Total fat in grams")
    total_fiber_g: float = Field(..., description="Total fiber in grams")
    macronutrient_distribution: MacronutrientDistribution = Field(..., description="Macronutrient percentages")
    warnings: List[CarbohydrateWarning] = Field(default_factory=list, description="Carbohydrate warnings")
    days_with_data: int = Field(..., description="Number of days with food entries")
    
    class Config:
        json_schema_extra = {
            "example": {
                "period": "weekly",
                "start_date": "2024-01-08",
                "end_date": "2024-01-14",
                "total_calories": 12850.5,
                "avg_daily_calories": 1835.8,
                "total_protein_g": 665.2,
                "total_carbohydrates_g": 1450.5,
                "total_fat_g": 435.3,
                "total_fiber_g": 198.5,
                "macronutrient_distribution": {
                    "protein_percent": 20.7,
                    "carbohydrates_percent": 45.2,
                    "fat_percent": 30.5
                },
                "warnings": [],
                "days_with_data": 7
            }
        }


class DailyTrendData(BaseModel):
    """Nutritional data for a single day in trend analysis."""
    
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    calories: float = Field(..., description="Total calories for the day")
    protein_g: float = Field(..., description="Total protein in grams")
    carbohydrates_g: float = Field(..., description="Total carbohydrates in grams")
    fat_g: float = Field(..., description="Total fat in grams")
    fiber_g: float = Field(..., description="Total fiber in grams")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-15",
                "calories": 1850.5,
                "protein_g": 95.2,
                "carbohydrates_g": 210.5,
                "fat_g": 62.3,
                "fiber_g": 28.5
            }
        }


class NutritionalTrendsResponse(BaseModel):
    """Nutritional trends over a date range."""
    
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    daily_data: List[DailyTrendData] = Field(..., description="Daily nutritional data")
    avg_calories: float = Field(..., description="Average daily calories over the period")
    avg_protein_g: float = Field(..., description="Average daily protein in grams")
    avg_carbohydrates_g: float = Field(..., description="Average daily carbohydrates in grams")
    avg_fat_g: float = Field(..., description="Average daily fat in grams")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "daily_data": [],
                "avg_calories": 1835.8,
                "avg_protein_g": 95.0,
                "avg_carbohydrates_g": 207.2,
                "avg_fat_g": 62.1
            }
        }
