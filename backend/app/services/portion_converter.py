"""
Portion size conversion service for unit conversions.

Handles conversion between different portion size units including:
- Weight units (grams, ounces, pounds)
- Volume units (cups, tablespoons, teaspoons, milliliters, liters)
- Piece-based units (pieces, slices, servings)
"""

import logging
from typing import Dict, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class PortionConverter:
    """Service for converting between different portion size units."""
    
    # Weight conversions (all to grams)
    WEIGHT_TO_GRAMS = {
        'g': 1.0,
        'gram': 1.0,
        'grams': 1.0,
        'kg': 1000.0,
        'kilogram': 1000.0,
        'kilograms': 1000.0,
        'oz': 28.3495,
        'ounce': 28.3495,
        'ounces': 28.3495,
        'lb': 453.592,
        'pound': 453.592,
        'pounds': 453.592,
    }
    
    # Volume conversions (all to milliliters)
    VOLUME_TO_ML = {
        'ml': 1.0,
        'milliliter': 1.0,
        'milliliters': 1.0,
        'l': 1000.0,
        'liter': 1000.0,
        'liters': 1.0,
        'cup': 236.588,
        'cups': 236.588,
        'tbsp': 14.7868,
        'tablespoon': 14.7868,
        'tablespoons': 14.7868,
        'tsp': 4.92892,
        'teaspoon': 4.92892,
        'teaspoons': 4.92892,
        'fl oz': 29.5735,
        'fluid ounce': 29.5735,
        'fluid ounces': 29.5735,
    }
    
    # Common food densities (g/ml) for volume-to-weight conversion
    FOOD_DENSITIES = {
        'water': 1.0,
        'milk': 1.03,
        'oil': 0.92,
        'flour': 0.593,
        'sugar': 0.845,
        'rice': 0.85,
        'butter': 0.911,
        'honey': 1.42,
        'default': 1.0  # Assume water density if unknown
    }
    
    def __init__(self):
        """Initialize the portion converter."""
        pass
    
    def convert(
        self,
        amount: float,
        from_unit: str,
        to_unit: str,
        food_density: Optional[float] = None
    ) -> float:
        """
        Convert amount from one unit to another.
        
        Args:
            amount: Amount to convert
            from_unit: Source unit (e.g., 'cup', 'oz', 'g')
            to_unit: Target unit (e.g., 'g', 'ml', 'tbsp')
            food_density: Optional density in g/ml for volume-weight conversions
            
        Returns:
            Converted amount
            
        Raises:
            ValueError: If units are incompatible or unknown
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        from_unit_lower = from_unit.lower().strip()
        to_unit_lower = to_unit.lower().strip()
        
        # Same unit - no conversion needed
        if from_unit_lower == to_unit_lower:
            return amount
        
        # Check if both are weight units
        if self._is_weight_unit(from_unit_lower) and self._is_weight_unit(to_unit_lower):
            return self._convert_weight(amount, from_unit_lower, to_unit_lower)
        
        # Check if both are volume units
        if self._is_volume_unit(from_unit_lower) and self._is_volume_unit(to_unit_lower):
            return self._convert_volume(amount, from_unit_lower, to_unit_lower)
        
        # Volume to weight or weight to volume (requires density)
        if self._is_volume_unit(from_unit_lower) and self._is_weight_unit(to_unit_lower):
            return self._convert_volume_to_weight(
                amount, from_unit_lower, to_unit_lower, food_density
            )
        
        if self._is_weight_unit(from_unit_lower) and self._is_volume_unit(to_unit_lower):
            return self._convert_weight_to_volume(
                amount, from_unit_lower, to_unit_lower, food_density
            )
        
        # Incompatible units
        raise ValueError(
            f"Cannot convert between '{from_unit}' and '{to_unit}': "
            f"incompatible unit types"
        )
    
    def _is_weight_unit(self, unit: str) -> bool:
        """Check if unit is a weight unit."""
        return unit in self.WEIGHT_TO_GRAMS
    
    def _is_volume_unit(self, unit: str) -> bool:
        """Check if unit is a volume unit."""
        return unit in self.VOLUME_TO_ML
    
    def _convert_weight(self, amount: float, from_unit: str, to_unit: str) -> float:
        """Convert between weight units."""
        # Convert to grams first
        grams = amount * self.WEIGHT_TO_GRAMS[from_unit]
        
        # Convert from grams to target unit
        result = grams / self.WEIGHT_TO_GRAMS[to_unit]
        
        logger.debug(
            f"Weight conversion: {amount} {from_unit} = {result} {to_unit}"
        )
        
        return result
    
    def _convert_volume(self, amount: float, from_unit: str, to_unit: str) -> float:
        """Convert between volume units."""
        # Convert to milliliters first
        ml = amount * self.VOLUME_TO_ML[from_unit]
        
        # Convert from milliliters to target unit
        result = ml / self.VOLUME_TO_ML[to_unit]
        
        logger.debug(
            f"Volume conversion: {amount} {from_unit} = {result} {to_unit}"
        )
        
        return result
    
    def _convert_volume_to_weight(
        self,
        amount: float,
        from_unit: str,
        to_unit: str,
        density: Optional[float] = None
    ) -> float:
        """Convert volume to weight using density."""
        if density is None:
            density = self.FOOD_DENSITIES['default']
            logger.warning(
                f"No density provided for volume-to-weight conversion, "
                f"using default density: {density} g/ml"
            )
        
        # Convert to milliliters
        ml = amount * self.VOLUME_TO_ML[from_unit]
        
        # Convert to grams using density
        grams = ml * density
        
        # Convert to target weight unit
        result = grams / self.WEIGHT_TO_GRAMS[to_unit]
        
        logger.debug(
            f"Volume-to-weight conversion: {amount} {from_unit} = "
            f"{result} {to_unit} (density: {density} g/ml)"
        )
        
        return result
    
    def _convert_weight_to_volume(
        self,
        amount: float,
        from_unit: str,
        to_unit: str,
        density: Optional[float] = None
    ) -> float:
        """Convert weight to volume using density."""
        if density is None:
            density = self.FOOD_DENSITIES['default']
            logger.warning(
                f"No density provided for weight-to-volume conversion, "
                f"using default density: {density} g/ml"
            )
        
        # Convert to grams
        grams = amount * self.WEIGHT_TO_GRAMS[from_unit]
        
        # Convert to milliliters using density
        ml = grams / density
        
        # Convert to target volume unit
        result = ml / self.VOLUME_TO_ML[to_unit]
        
        logger.debug(
            f"Weight-to-volume conversion: {amount} {from_unit} = "
            f"{result} {to_unit} (density: {density} g/ml)"
        )
        
        return result
    
    def get_supported_units(self) -> Dict[str, list]:
        """
        Get list of supported units by category.
        
        Returns:
            Dictionary with 'weight' and 'volume' keys containing unit lists
        """
        return {
            'weight': list(set(self.WEIGHT_TO_GRAMS.keys())),
            'volume': list(set(self.VOLUME_TO_ML.keys()))
        }
    
    def get_food_density(self, food_type: str) -> float:
        """
        Get density for a food type.
        
        Args:
            food_type: Type of food (e.g., 'milk', 'flour')
            
        Returns:
            Density in g/ml
        """
        food_type_lower = food_type.lower().strip()
        return self.FOOD_DENSITIES.get(food_type_lower, self.FOOD_DENSITIES['default'])


class CommonServingSizes:
    """Common serving sizes for different food categories."""
    
    SERVING_SIZES = {
        'Poultry Products': [
            {'unit': 'g', 'amount': 100, 'description': '100g (standard)'},
            {'unit': 'oz', 'amount': 3, 'description': '3 oz'},
            {'unit': 'oz', 'amount': 4, 'description': '4 oz (small breast)'},
            {'unit': 'oz', 'amount': 6, 'description': '6 oz (large breast)'},
        ],
        'Dairy and Egg Products': [
            {'unit': 'g', 'amount': 100, 'description': '100g (standard)'},
            {'unit': 'cup', 'amount': 1, 'description': '1 cup'},
            {'unit': 'tbsp', 'amount': 1, 'description': '1 tablespoon'},
            {'unit': 'oz', 'amount': 1, 'description': '1 oz'},
        ],
        'Vegetables and Vegetable Products': [
            {'unit': 'g', 'amount': 100, 'description': '100g (standard)'},
            {'unit': 'cup', 'amount': 1, 'description': '1 cup'},
            {'unit': 'cup', 'amount': 0.5, 'description': '1/2 cup'},
        ],
        'Fruits and Fruit Juices': [
            {'unit': 'g', 'amount': 100, 'description': '100g (standard)'},
            {'unit': 'cup', 'amount': 1, 'description': '1 cup'},
            {'unit': 'piece', 'amount': 1, 'description': '1 piece'},
        ],
        'Cereal Grains and Pasta': [
            {'unit': 'g', 'amount': 100, 'description': '100g (standard)'},
            {'unit': 'cup', 'amount': 1, 'description': '1 cup cooked'},
            {'unit': 'cup', 'amount': 0.5, 'description': '1/2 cup cooked'},
        ],
        'default': [
            {'unit': 'g', 'amount': 100, 'description': '100g (standard)'},
            {'unit': 'oz', 'amount': 1, 'description': '1 oz'},
            {'unit': 'cup', 'amount': 1, 'description': '1 cup'},
        ]
    }
    
    @classmethod
    def get_serving_sizes(cls, category: str) -> list:
        """
        Get common serving sizes for a food category.
        
        Args:
            category: Food category
            
        Returns:
            List of serving size dictionaries
        """
        return cls.SERVING_SIZES.get(category, cls.SERVING_SIZES['default'])
