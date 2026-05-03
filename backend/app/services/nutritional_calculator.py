"""
Nutritional calculator service for calorie and nutrient calculations.

This service handles portion-based nutritional calculations including:
- Calorie calculations
- Macronutrient calculations (proteins, carbohydrates, fats)
- Micronutrient calculations (vitamins, minerals)
- Meal-level nutritional summation
- Standard unit formatting
"""

import logging
from typing import Dict, List, Optional
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import Food, Nutrient, FoodNutrient

logger = logging.getLogger(__name__)


class NutritionalCalculator:
    """Service for calculating nutritional values based on portion sizes."""
    
    def __init__(self, db: Session):
        """
        Initialize the nutritional calculator.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def calculate_food_nutrition(
        self,
        food_id: UUID,
        quantity_grams: float
    ) -> Dict[str, float]:
        """
        Calculate nutritional values for a specific food and quantity.
        
        Args:
            food_id: UUID of the food item
            quantity_grams: Quantity in grams
            
        Returns:
            Dictionary with nutritional values:
            {
                'calories': float,
                'protein_g': float,
                'carbohydrates_g': float,
                'fat_g': float,
                'fiber_g': float,
                'vitamins': {...},
                'minerals': {...}
            }
        """
        if quantity_grams <= 0:
            raise ValueError("Quantity must be positive")
        
        # Get all nutrients for this food
        nutrients = self._get_food_nutrients(food_id)
        
        if not nutrients:
            logger.warning(f"No nutritional data found for food_id: {food_id}")
            # Try to get food details to see if it exists
            from app.models import Food
            food = self.db.query(Food).filter(Food.food_id == food_id).first()
            if food:
                logger.warning(f"Food exists: {food.name} (category: {food.category}, type: {food.food_type})")
            else:
                logger.warning(f"Food with ID {food_id} does not exist in database")
            return self._empty_nutrition_dict()
        
        logger.info(f"Found {len(nutrients)} nutrients for food_id: {food_id}")
        for nutrient_name, amount, unit, nutrient_type in nutrients:
            logger.info(f"  - {nutrient_name}: {amount} {unit} (type: {nutrient_type})")
        
        # Calculate proportional values based on quantity
        nutrition = self._empty_nutrition_dict()
        
        for nutrient_name, amount_per_100g, unit, nutrient_type in nutrients:
            # Calculate amount for given quantity
            calculated_amount = self._calculate_proportional_amount(
                amount_per_100g, 
                quantity_grams
            )
            
            # Categorize and store the nutrient
            self._categorize_nutrient(
                nutrition,
                nutrient_name,
                calculated_amount,
                unit,
                nutrient_type
            )
        
        logger.debug(
            f"Calculated nutrition for food_id={food_id}, "
            f"quantity={quantity_grams}g: {nutrition['calories']} kcal"
        )
        
        return nutrition
    
    def calculate_meal_nutrition(
        self,
        food_items: List[Dict[str, any]]
    ) -> Dict[str, float]:
        """
        Calculate total nutritional values for a meal (multiple food items).
        
        Args:
            food_items: List of dicts with 'food_id' and 'quantity_grams'
            Example: [
                {'food_id': uuid1, 'quantity_grams': 100},
                {'food_id': uuid2, 'quantity_grams': 50}
            ]
            
        Returns:
            Dictionary with summed nutritional values
        """
        if not food_items:
            return self._empty_nutrition_dict()
        
        # Initialize totals
        meal_nutrition = self._empty_nutrition_dict()
        
        # Sum nutrition from each food item
        for item in food_items:
            food_id = item.get('food_id')
            quantity = item.get('quantity_grams', 0)
            
            if not food_id or quantity <= 0:
                logger.warning(f"Invalid food item: {item}")
                continue
            
            # Calculate nutrition for this food
            food_nutrition = self.calculate_food_nutrition(food_id, quantity)
            
            # Add to meal totals
            meal_nutrition = self._sum_nutrition(meal_nutrition, food_nutrition)
        
        logger.info(
            f"Calculated meal nutrition for {len(food_items)} items: "
            f"{meal_nutrition['calories']} kcal"
        )
        
        return meal_nutrition
    
    def format_nutrition_display(
        self,
        nutrition: Dict[str, float]
    ) -> Dict[str, str]:
        """
        Format nutritional values for display with standard units.
        
        Args:
            nutrition: Dictionary with nutritional values
            
        Returns:
            Dictionary with formatted strings:
            {
                'calories': '250 kcal',
                'protein': '15.5 g',
                'carbohydrates': '30.2 g',
                ...
            }
        """
        formatted = {}
        
        # Format calories
        formatted['calories'] = f"{nutrition['calories']:.1f} kcal"
        
        # Format macronutrients (grams)
        macros = ['protein_g', 'carbohydrates_g', 'fat_g', 'fiber_g']
        for macro in macros:
            value = nutrition.get(macro, 0)
            key = macro.replace('_g', '')
            formatted[key] = f"{value:.1f} g"
        
        # Format vitamins
        formatted['vitamins'] = {}
        for vitamin, value in nutrition.get('vitamins', {}).items():
            formatted['vitamins'][vitamin] = self._format_micronutrient(
                value,
                self._get_vitamin_unit(vitamin)
            )
        
        # Format minerals
        formatted['minerals'] = {}
        for mineral, value in nutrition.get('minerals', {}).items():
            formatted['minerals'][mineral] = self._format_micronutrient(
                value,
                self._get_mineral_unit(mineral)
            )
        
        return formatted
    
    def _get_food_nutrients(self, food_id: UUID) -> List[tuple]:
        """
        Get all nutrients for a food from database.
        
        Returns:
            List of tuples: (nutrient_name, amount, unit, nutrient_type)
        """
        results = self.db.query(
            Nutrient.name,
            FoodNutrient.amount,
            Nutrient.unit,
            Nutrient.nutrient_type
        ).join(
            FoodNutrient, Nutrient.nutrient_id == FoodNutrient.nutrient_id
        ).filter(
            FoodNutrient.food_id == food_id
        ).all()
        
        return results
    
    def _calculate_proportional_amount(
        self,
        amount_per_100g: Decimal,
        quantity_grams: float
    ) -> float:
        """
        Calculate proportional nutrient amount based on quantity.
        
        Formula: (amount_per_100g * quantity_grams) / 100
        
        Args:
            amount_per_100g: Nutrient amount per 100g
            quantity_grams: Actual quantity in grams
            
        Returns:
            Calculated amount for the given quantity
        """
        return (float(amount_per_100g) * quantity_grams) / 100.0
    
    def _categorize_nutrient(
        self,
        nutrition: Dict,
        nutrient_name: str,
        amount: float,
        unit: str,
        nutrient_type: str
    ):
        """
        Categorize and store nutrient in the appropriate section.
        
        Args:
            nutrition: Nutrition dictionary to update
            nutrient_name: Name of the nutrient
            amount: Calculated amount
            unit: Unit of measurement
            nutrient_type: Type (macronutrient, vitamin, mineral, other)
        """
        name_lower = nutrient_name.lower()
        
        # Calories/Energy
        if 'energy' in name_lower or 'calorie' in name_lower:
            if unit.upper() == 'KCAL':
                nutrition['calories'] += amount
        
        # Macronutrients
        elif 'protein' in name_lower:
            nutrition['protein_g'] += amount
        elif 'carbohydrate' in name_lower or 'carb' in name_lower:
            nutrition['carbohydrates_g'] += amount
        elif 'fat' in name_lower and 'fatty' not in name_lower:
            nutrition['fat_g'] += amount
        elif 'fiber' in name_lower or 'fibre' in name_lower:
            nutrition['fiber_g'] += amount
        
        # Vitamins
        elif nutrient_type == 'vitamin' or 'vitamin' in name_lower:
            nutrition['vitamins'][nutrient_name] = amount
        
        # Minerals
        elif nutrient_type == 'mineral' or any(
            mineral in name_lower for mineral in [
                'calcium', 'iron', 'magnesium', 'phosphorus', 
                'potassium', 'sodium', 'zinc', 'copper', 'selenium'
            ]
        ):
            nutrition['minerals'][nutrient_name] = amount
    
    def _sum_nutrition(
        self,
        nutrition1: Dict,
        nutrition2: Dict
    ) -> Dict:
        """
        Sum two nutrition dictionaries.
        
        Args:
            nutrition1: First nutrition dict
            nutrition2: Second nutrition dict
            
        Returns:
            Combined nutrition dict with summed values
        """
        result = self._empty_nutrition_dict()
        
        # Sum basic nutrients
        for key in ['calories', 'protein_g', 'carbohydrates_g', 'fat_g', 'fiber_g']:
            result[key] = nutrition1.get(key, 0) + nutrition2.get(key, 0)
        
        # Sum vitamins
        all_vitamins = set(nutrition1.get('vitamins', {}).keys()) | \
                      set(nutrition2.get('vitamins', {}).keys())
        for vitamin in all_vitamins:
            result['vitamins'][vitamin] = \
                nutrition1.get('vitamins', {}).get(vitamin, 0) + \
                nutrition2.get('vitamins', {}).get(vitamin, 0)
        
        # Sum minerals
        all_minerals = set(nutrition1.get('minerals', {}).keys()) | \
                      set(nutrition2.get('minerals', {}).keys())
        for mineral in all_minerals:
            result['minerals'][mineral] = \
                nutrition1.get('minerals', {}).get(mineral, 0) + \
                nutrition2.get('minerals', {}).get(mineral, 0)
        
        return result
    
    def _empty_nutrition_dict(self) -> Dict:
        """Create an empty nutrition dictionary with default structure."""
        return {
            'calories': 0.0,
            'protein_g': 0.0,
            'carbohydrates_g': 0.0,
            'fat_g': 0.0,
            'fiber_g': 0.0,
            'vitamins': {},
            'minerals': {}
        }
    
    def _format_micronutrient(self, value: float, unit: str) -> str:
        """Format micronutrient value with appropriate precision."""
        if value >= 1000:
            # Convert to larger unit if applicable
            if unit.lower() in ['mg', 'milligram']:
                return f"{value/1000:.2f} g"
            elif unit.lower() in ['mcg', 'µg', 'microgram']:
                return f"{value/1000:.2f} mg"
        
        if value >= 1:
            return f"{value:.1f} {unit}"
        else:
            return f"{value:.2f} {unit}"
    
    def _get_vitamin_unit(self, vitamin_name: str) -> str:
        """Get standard unit for vitamin display."""
        # Most vitamins are measured in mg or mcg
        if any(v in vitamin_name.upper() for v in ['A', 'D', 'E', 'K', 'B12']):
            return 'mcg'
        return 'mg'
    
    def _get_mineral_unit(self, mineral_name: str) -> str:
        """Get standard unit for mineral display."""
        # Most minerals are measured in mg
        return 'mg'
