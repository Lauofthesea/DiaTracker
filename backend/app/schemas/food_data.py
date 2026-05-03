"""
Pydantic schemas for food data parsing and validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal


class FoodCSVRow(BaseModel):
    """Schema for food.csv row."""
    
    fdc_id: str = Field(..., description="FDC ID from USDA database")
    data_type: str = Field(..., description="Type of food data")
    description: str = Field(..., description="Food description/name")
    food_category_id: Optional[str] = Field(None, description="Category ID")
    publication_date: Optional[str] = Field(None, description="Publication date")
    
    @field_validator('fdc_id', 'description')
    @classmethod
    def not_empty(cls, v: str) -> str:
        """Validate that required fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class NutrientCSVRow(BaseModel):
    """Schema for nutrient.csv row."""
    
    id: str = Field(..., description="Nutrient ID")
    name: str = Field(..., description="Nutrient name")
    unit_name: str = Field(..., description="Unit of measurement")
    nutrient_nbr: Optional[str] = Field(None, description="Nutrient number")
    rank: Optional[str] = Field(None, description="Display rank")
    
    @field_validator('id', 'name', 'unit_name')
    @classmethod
    def not_empty(cls, v: str) -> str:
        """Validate that required fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class FoodNutrientCSVRow(BaseModel):
    """Schema for food_nutrient.csv row."""
    
    id: str = Field(..., description="Record ID")
    fdc_id: str = Field(..., description="Food FDC ID")
    nutrient_id: str = Field(..., description="Nutrient ID")
    amount: str = Field(..., description="Amount of nutrient")
    data_points: Optional[str] = Field(None, description="Number of data points")
    derivation_id: Optional[str] = Field(None, description="Derivation ID")
    min: Optional[str] = Field(None, description="Minimum value")
    max: Optional[str] = Field(None, description="Maximum value")
    median: Optional[str] = Field(None, description="Median value")
    footnote: Optional[str] = Field(None, description="Footnote")
    min_year_acquired: Optional[str] = Field(None, description="Minimum year acquired")
    
    @field_validator('fdc_id', 'nutrient_id', 'amount')
    @classmethod
    def not_empty(cls, v: str) -> str:
        """Validate that required fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: str) -> str:
        """Validate that amount is a valid number."""
        try:
            float(v)
        except ValueError:
            raise ValueError(f"Amount must be a valid number, got: {v}")
        return v


class FoodDataCSVRow(BaseModel):
    """Schema for FoodData.csv row."""
    
    Class: str = Field(..., alias="Class", description="Food class")
    Type: str = Field(..., alias="Type", description="Food type")
    Group: str = Field(..., alias="Group", description="Food group")
    Food: str = Field(..., description="Food name")
    Allergy: Optional[str] = Field(None, alias="Allergy", description="Allergy information")
    
    class Config:
        populate_by_name = True
    
    @field_validator('Class', 'Type', 'Group', 'Food')
    @classmethod
    def not_empty(cls, v: str) -> str:
        """Validate that required fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class ParsedFood(BaseModel):
    """Parsed food data structure."""
    
    fdc_id: str
    name: str
    description: Optional[str] = None
    category: str
    food_type: Optional[str] = None
    allergens: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "fdc_id": "319877",
                "name": "Hummus",
                "description": "HUMMUS, SABRA CLASSIC",
                "category": "Legumes",
                "food_type": "Prepared",
                "allergens": ["Sesame"]
            }
        }


class ParsedNutrient(BaseModel):
    """Parsed nutrient data structure."""
    
    nutrient_id: str
    name: str
    unit: str
    nutrient_type: str
    
    @field_validator('nutrient_type')
    @classmethod
    def validate_nutrient_type(cls, v: str) -> str:
        """Validate nutrient type."""
        valid_types = ['macronutrient', 'vitamin', 'mineral', 'other']
        if v not in valid_types:
            return 'other'
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "nutrient_id": "1003",
                "name": "Protein",
                "unit": "G",
                "nutrient_type": "macronutrient"
            }
        }


class ParsedFoodNutrient(BaseModel):
    """Parsed food-nutrient relationship."""
    
    fdc_id: str
    nutrient_id: str
    amount: Decimal
    per_unit: str = "100g"
    
    @field_validator('amount', mode='before')
    @classmethod
    def convert_to_decimal(cls, v: Any) -> Decimal:
        """Convert amount to Decimal."""
        if isinstance(v, Decimal):
            return v
        try:
            return Decimal(str(v))
        except Exception as e:
            raise ValueError(f"Cannot convert amount to Decimal: {v}") from e
    
    class Config:
        json_schema_extra = {
            "example": {
                "fdc_id": "319877",
                "nutrient_id": "1003",
                "amount": "7.5",
                "per_unit": "100g"
            }
        }


class ParsedFoodData(BaseModel):
    """Complete parsed food database."""
    
    foods: List[ParsedFood] = Field(default_factory=list)
    nutrients: List[ParsedNutrient] = Field(default_factory=list)
    food_nutrients: List[ParsedFoodNutrient] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "foods": [],
                "nutrients": [],
                "food_nutrients": []
            }
        }


class CSVParseError(BaseModel):
    """CSV parsing error information."""
    
    file_name: str
    row_number: int
    error_message: str
    row_data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_name": "food.csv",
                "row_number": 42,
                "error_message": "Missing required field: description",
                "row_data": {"fdc_id": "123", "description": ""}
            }
        }


class CSVParseResult(BaseModel):
    """Result of CSV parsing operation."""
    
    success: bool
    data: Optional[ParsedFoodData] = None
    errors: List[CSVParseError] = Field(default_factory=list)
    total_rows_processed: int = 0
    successful_rows: int = 0
    failed_rows: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"foods": [], "nutrients": [], "food_nutrients": []},
                "errors": [],
                "total_rows_processed": 1000,
                "successful_rows": 995,
                "failed_rows": 5
            }
        }
