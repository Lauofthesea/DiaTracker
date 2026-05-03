"""
CSV food data parser service.

This module provides functionality to parse food-related CSV files
and validate the data according to the schema requirements.
"""

import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from decimal import Decimal

from app.schemas.food_data import (
    FoodCSVRow,
    NutrientCSVRow,
    FoodNutrientCSVRow,
    FoodDataCSVRow,
    ParsedFood,
    ParsedNutrient,
    ParsedFoodNutrient,
    ParsedFoodData,
    CSVParseError,
    CSVParseResult,
)

logger = logging.getLogger(__name__)


class FoodDataParser:
    """Parser for food database CSV files."""
    
    # Category mapping from food_category_id to category name
    CATEGORY_MAP = {
        "1": "Dairy and Egg Products",
        "2": "Spices and Herbs",
        "3": "Baby Foods",
        "4": "Fats and Oils",
        "5": "Poultry Products",
        "6": "Soups, Sauces, and Gravies",
        "7": "Sausages and Luncheon Meats",
        "8": "Breakfast Cereals",
        "9": "Fruits and Fruit Juices",
        "10": "Pork Products",
        "11": "Vegetables and Vegetable Products",
        "12": "Nut and Seed Products",
        "13": "Beef Products",
        "14": "Beverages",
        "15": "Finfish and Shellfish Products",
        "16": "Legumes and Legume Products",
        "17": "Lamb, Veal, and Game Products",
        "18": "Baked Products",
        "19": "Sweets",
        "20": "Cereal Grains and Pasta",
        "21": "Fast Foods",
        "22": "Meals, Entrees, and Side Dishes",
        "25": "Snacks",
    }
    
    # Nutrient type classification
    MACRONUTRIENTS = {
        "Protein", "Total lipid (fat)", "Carbohydrate", "Energy", 
        "Fiber", "Sugars", "Water", "Ash"
    }
    
    VITAMINS = {
        "Vitamin A", "Vitamin C", "Vitamin D", "Vitamin E", "Vitamin K",
        "Thiamin", "Riboflavin", "Niacin", "Vitamin B-6", "Folate",
        "Vitamin B-12", "Pantothenic acid", "Biotin", "Choline"
    }
    
    MINERALS = {
        "Calcium", "Iron", "Magnesium", "Phosphorus", "Potassium",
        "Sodium", "Zinc", "Copper", "Manganese", "Selenium",
        "Fluoride", "Chromium", "Molybdenum", "Iodine"
    }
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the parser.
        
        Args:
            data_dir: Directory containing CSV files. Defaults to project root.
        """
        self.data_dir = data_dir or Path(".")
        self.errors: List[CSVParseError] = []
    
    def _classify_nutrient_type(self, nutrient_name: str) -> str:
        """
        Classify nutrient into type category.
        
        Args:
            nutrient_name: Name of the nutrient
            
        Returns:
            Nutrient type: 'macronutrient', 'vitamin', 'mineral', or 'other'
        """
        # Check for exact matches first
        if nutrient_name in self.MACRONUTRIENTS:
            return "macronutrient"
        if nutrient_name in self.VITAMINS:
            return "vitamin"
        if nutrient_name in self.MINERALS:
            return "mineral"
        
        # Check for partial matches
        name_lower = nutrient_name.lower()
        if any(macro.lower() in name_lower for macro in self.MACRONUTRIENTS):
            return "macronutrient"
        if any(vit.lower() in name_lower for vit in self.VITAMINS):
            return "vitamin"
        if any(min.lower() in name_lower for min in self.MINERALS):
            return "mineral"
        
        return "other"
    
    def _log_error(
        self, 
        file_name: str, 
        row_number: int, 
        error_message: str, 
        row_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a parsing error.
        
        Args:
            file_name: Name of the CSV file
            row_number: Row number where error occurred
            error_message: Description of the error
            row_data: Optional row data for debugging
        """
        error = CSVParseError(
            file_name=file_name,
            row_number=row_number,
            error_message=error_message,
            row_data=row_data
        )
        self.errors.append(error)
        logger.warning(
            f"CSV Parse Error in {file_name} at row {row_number}: {error_message}"
        )
    
    def _validate_csv_columns(
        self, 
        file_path: Path, 
        required_columns: List[str]
    ) -> bool:
        """
        Validate that CSV file has all required columns.
        
        Args:
            file_path: Path to CSV file
            required_columns: List of required column names
            
        Returns:
            True if all columns present, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    self._log_error(
                        file_path.name, 
                        0, 
                        "CSV file has no header row"
                    )
                    return False
                
                missing_columns = set(required_columns) - set(reader.fieldnames)
                if missing_columns:
                    self._log_error(
                        file_path.name,
                        0,
                        f"Missing required columns: {', '.join(missing_columns)}"
                    )
                    return False
                
                return True
        except Exception as e:
            self._log_error(
                file_path.name,
                0,
                f"Error reading CSV file: {str(e)}"
            )
            return False
    
    def parse_food_csv(self, file_path: Optional[Path] = None) -> List[ParsedFood]:
        """
        Parse food.csv file.
        
        Args:
            file_path: Path to food.csv file
            
        Returns:
            List of parsed food items
        """
        if file_path is None:
            file_path = self.data_dir / "food.csv"
        
        required_columns = ["fdc_id", "data_type", "description", "food_category_id"]
        if not self._validate_csv_columns(file_path, required_columns):
            return []
        
        foods = []
        row_number = 1  # Start at 1 (header is row 0)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    row_number += 1
                    try:
                        # Validate row with Pydantic
                        csv_row = FoodCSVRow(**row)
                        
                        # Map to ParsedFood
                        category = self.CATEGORY_MAP.get(
                            csv_row.food_category_id or "", 
                            "Other"
                        )
                        
                        food = ParsedFood(
                            fdc_id=csv_row.fdc_id,
                            name=csv_row.description,
                            description=csv_row.description,
                            category=category,
                            food_type=csv_row.data_type,
                            allergens=[]  # Will be populated from FoodData.csv
                        )
                        foods.append(food)
                        
                    except Exception as e:
                        self._log_error(
                            file_path.name,
                            row_number,
                            str(e),
                            row
                        )
                        continue
        
        except Exception as e:
            self._log_error(
                file_path.name,
                0,
                f"Error opening file: {str(e)}"
            )
        
        logger.info(f"Parsed {len(foods)} foods from {file_path.name}")
        return foods
    
    def parse_nutrient_csv(
        self, 
        file_path: Optional[Path] = None
    ) -> List[ParsedNutrient]:
        """
        Parse nutrient.csv file.
        
        Args:
            file_path: Path to nutrient.csv file
            
        Returns:
            List of parsed nutrients
        """
        if file_path is None:
            file_path = self.data_dir / "nutrient.csv"
        
        required_columns = ["id", "name", "unit_name"]
        if not self._validate_csv_columns(file_path, required_columns):
            return []
        
        nutrients = []
        row_number = 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    row_number += 1
                    try:
                        # Validate row with Pydantic
                        csv_row = NutrientCSVRow(**row)
                        
                        # Classify nutrient type
                        nutrient_type = self._classify_nutrient_type(csv_row.name)
                        
                        # Map to ParsedNutrient
                        nutrient = ParsedNutrient(
                            nutrient_id=csv_row.id,
                            name=csv_row.name,
                            unit=csv_row.unit_name,
                            nutrient_type=nutrient_type
                        )
                        nutrients.append(nutrient)
                        
                    except Exception as e:
                        self._log_error(
                            file_path.name,
                            row_number,
                            str(e),
                            row
                        )
                        continue
        
        except Exception as e:
            self._log_error(
                file_path.name,
                0,
                f"Error opening file: {str(e)}"
            )
        
        logger.info(f"Parsed {len(nutrients)} nutrients from {file_path.name}")
        return nutrients
    
    def parse_food_nutrient_csv(
        self, 
        file_path: Optional[Path] = None
    ) -> List[ParsedFoodNutrient]:
        """
        Parse food_nutrient.csv file.
        
        Args:
            file_path: Path to food_nutrient.csv file
            
        Returns:
            List of parsed food-nutrient relationships
        """
        if file_path is None:
            file_path = self.data_dir / "food_nutrient.csv"
        
        required_columns = ["fdc_id", "nutrient_id", "amount"]
        if not self._validate_csv_columns(file_path, required_columns):
            return []
        
        food_nutrients = []
        row_number = 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    row_number += 1
                    try:
                        # Validate row with Pydantic
                        csv_row = FoodNutrientCSVRow(**row)
                        
                        # Map to ParsedFoodNutrient
                        food_nutrient = ParsedFoodNutrient(
                            fdc_id=csv_row.fdc_id,
                            nutrient_id=csv_row.nutrient_id,
                            amount=Decimal(csv_row.amount),
                            per_unit="100g"
                        )
                        food_nutrients.append(food_nutrient)
                        
                    except Exception as e:
                        self._log_error(
                            file_path.name,
                            row_number,
                            str(e),
                            row
                        )
                        continue
        
        except Exception as e:
            self._log_error(
                file_path.name,
                0,
                f"Error opening file: {str(e)}"
            )
        
        logger.info(
            f"Parsed {len(food_nutrients)} food-nutrient relationships "
            f"from {file_path.name}"
        )
        return food_nutrients
    
    def parse_food_data_csv(
        self, 
        file_path: Optional[Path] = None
    ) -> Dict[str, List[str]]:
        """
        Parse FoodData.csv file for allergen information.
        
        Args:
            file_path: Path to FoodData.csv file
            
        Returns:
            Dictionary mapping food names to allergen lists
        """
        if file_path is None:
            file_path = self.data_dir / "FoodData.csv"
        
        required_columns = ["Class", "Type", "Group", "Food"]
        if not self._validate_csv_columns(file_path, required_columns):
            return {}
        
        food_allergens = {}
        row_number = 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    row_number += 1
                    try:
                        # Validate row with Pydantic
                        csv_row = FoodDataCSVRow(**row)
                        
                        # Extract allergen information
                        allergens = []
                        if csv_row.Allergy and csv_row.Allergy.strip():
                            allergens = [
                                a.strip() 
                                for a in csv_row.Allergy.split(',')
                                if a.strip()
                            ]
                        
                        food_allergens[csv_row.Food.lower()] = allergens
                        
                    except Exception as e:
                        self._log_error(
                            file_path.name,
                            row_number,
                            str(e),
                            row
                        )
                        continue
        
        except Exception as e:
            self._log_error(
                file_path.name,
                0,
                f"Error opening file: {str(e)}"
            )
        
        logger.info(
            f"Parsed allergen information for {len(food_allergens)} foods "
            f"from {file_path.name}"
        )
        return food_allergens
    
    def parse_all(self) -> CSVParseResult:
        """
        Parse all CSV files and combine the data.
        
        Returns:
            CSVParseResult with parsed data and any errors
        """
        self.errors = []  # Reset errors
        
        logger.info("Starting CSV parsing...")
        
        # Parse all files
        foods = self.parse_food_csv()
        nutrients = self.parse_nutrient_csv()
        food_nutrients = self.parse_food_nutrient_csv()
        food_allergens = self.parse_food_data_csv()
        
        # Enrich foods with allergen information
        for food in foods:
            food_name_lower = food.name.lower()
            # Try exact match first
            if food_name_lower in food_allergens:
                food.allergens = food_allergens[food_name_lower]
            else:
                # Try partial match
                for allergen_food, allergens in food_allergens.items():
                    if allergen_food in food_name_lower or food_name_lower in allergen_food:
                        food.allergens = allergens
                        break
        
        # Create result
        total_rows = len(foods) + len(nutrients) + len(food_nutrients)
        failed_rows = len(self.errors)
        successful_rows = total_rows - failed_rows
        
        result = CSVParseResult(
            success=len(self.errors) == 0,
            data=ParsedFoodData(
                foods=foods,
                nutrients=nutrients,
                food_nutrients=food_nutrients
            ),
            errors=self.errors,
            total_rows_processed=total_rows + failed_rows,
            successful_rows=successful_rows,
            failed_rows=failed_rows
        )
        
        logger.info(
            f"CSV parsing complete. "
            f"Processed: {result.total_rows_processed}, "
            f"Successful: {result.successful_rows}, "
            f"Failed: {result.failed_rows}"
        )
        
        return result
