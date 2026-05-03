"""
Food service for search and filtering operations.
"""

import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, text
from uuid import UUID

from app.models import Food, Nutrient, FoodNutrient
from app.schemas.food import (
    FoodSearchResult,
    FoodDetail,
    NutrientInfo,
)

logger = logging.getLogger(__name__)


class FoodService:
    """Service for food search and filtering operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the food service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def search_foods(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        exclude_allergens: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[FoodSearchResult], int]:
        """
        Search and filter foods with pagination.
        
        Args:
            query: Text search query
            category: Filter by category
            exclude_allergens: List of allergens to exclude
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (list of food results, total count)
        """
        # Build base query
        db_query = self.db.query(Food)
        
        # Apply text search
        if query and query.strip():
            search_query = query.strip()
            
            # Check database dialect for appropriate search method
            dialect_name = self.db.bind.dialect.name
            
            if dialect_name == 'postgresql':
                # Use PostgreSQL full-text search with relevance ranking
                db_query = db_query.filter(
                    func.to_tsvector('english', Food.name).op('@@')(
                        func.plainto_tsquery('english', search_query)
                    )
                ).order_by(
                    func.ts_rank(
                        func.to_tsvector('english', Food.name),
                        func.plainto_tsquery('english', search_query)
                    ).desc()
                )
            else:
                # Fallback to LIKE search for other databases (e.g., SQLite for testing)
                db_query = db_query.filter(
                    Food.name.ilike(f'%{search_query}%')
                ).order_by(Food.name)
        else:
            # Default ordering by name
            db_query = db_query.order_by(Food.name)
        
        # Apply category filter (supports comma-separated categories)
        if category:
            categories = [c.strip() for c in category.split(',') if c.strip()]
            if categories:
                db_query = db_query.filter(Food.category.in_(categories))
        
        # Apply allergen filter (exclude foods with specified allergens)
        if exclude_allergens:
            dialect_name = self.db.bind.dialect.name
            
            if dialect_name == 'postgresql':
                # PostgreSQL array operations
                for allergen in exclude_allergens:
                    db_query = db_query.filter(
                        or_(
                            Food.allergens.is_(None),
                            ~Food.allergens.any(allergen)
                        )
                    )
            else:
                # For SQLite and other databases, check if allergen list contains the value
                # This is a simplified approach for testing
                for allergen in exclude_allergens:
                    db_query = db_query.filter(
                        or_(
                            Food.allergens.is_(None),
                            ~Food.allergens.contains([allergen])
                        )
                    )
        
        # Get total count before pagination
        total = db_query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        foods = db_query.offset(offset).limit(page_size).all()
        
        # Convert to response schema
        results = []
        for food in foods:
            # Get calories from nutrients (Energy nutrient)
            calories = self._get_food_calories(food.food_id)
            
            result = FoodSearchResult(
                food_id=food.food_id,
                name=food.name,
                category=food.category,
                food_type=food.food_type,
                allergens=food.allergens,
                calories_per_serving=calories
            )
            results.append(result)
        
        logger.info(
            f"Food search: query='{query}', category='{category}', "
            f"found {total} results, returning page {page}"
        )
        
        return results, total
    
    def get_food_by_id(self, food_id: UUID) -> Optional[FoodDetail]:
        """
        Get detailed food information by ID.
        
        Args:
            food_id: Food UUID
            
        Returns:
            FoodDetail or None if not found
        """
        food = self.db.query(Food).filter(Food.food_id == food_id).first()
        
        if not food:
            return None
        
        # Get nutrients
        nutrients = self._get_food_nutrients(food_id)
        
        detail = FoodDetail(
            food_id=food.food_id,
            name=food.name,
            description=food.description,
            category=food.category,
            food_type=food.food_type,
            allergens=food.allergens,
            nutrients=nutrients,
            created_at=food.created_at
        )
        
        return detail
    
    def get_categories(self) -> List[str]:
        """
        Get list of all food categories.
        
        Returns:
            List of category names
        """
        categories = self.db.query(Food.category).distinct().order_by(Food.category).all()
        return [cat[0] for cat in categories]
    
    def _get_food_calories(self, food_id: UUID) -> Optional[float]:
        """
        Get calories for a food (per 100g).
        
        Args:
            food_id: Food UUID
            
        Returns:
            Calories per 100g or None
        """
        # Query for Energy nutrient
        result = self.db.query(FoodNutrient.amount).join(
            Nutrient, FoodNutrient.nutrient_id == Nutrient.nutrient_id
        ).filter(
            FoodNutrient.food_id == food_id,
            or_(
                Nutrient.name.ilike('%energy%'),
                Nutrient.name.ilike('%calorie%')
            ),
            Nutrient.unit.ilike('KCAL')
        ).first()
        
        if result:
            return float(result[0])
        return None
    
    def _get_food_nutrients(self, food_id: UUID) -> List[NutrientInfo]:
        """
        Get all nutrients for a food.
        
        Args:
            food_id: Food UUID
            
        Returns:
            List of nutrient information
        """
        results = self.db.query(
            Nutrient.nutrient_id,
            Nutrient.name,
            FoodNutrient.amount,
            Nutrient.unit,
            FoodNutrient.per_unit
        ).join(
            FoodNutrient, Nutrient.nutrient_id == FoodNutrient.nutrient_id
        ).filter(
            FoodNutrient.food_id == food_id
        ).order_by(Nutrient.name).all()
        
        nutrients = []
        for result in results:
            nutrient = NutrientInfo(
                nutrient_id=result[0],
                name=result[1],
                amount=result[2],
                unit=result[3],
                per_unit=result[4]
            )
            nutrients.append(nutrient)
        
        return nutrients
    
    def search_foods_by_name(
        self,
        name_query: str,
        limit: int = 10
    ) -> List[FoodSearchResult]:
        """
        Quick search foods by name (for autocomplete).
        
        Args:
            name_query: Partial name to search
            limit: Maximum number of results
            
        Returns:
            List of matching foods
        """
        foods = self.db.query(Food).filter(
            Food.name.ilike(f'%{name_query}%')
        ).order_by(Food.name).limit(limit).all()
        
        results = []
        for food in foods:
            calories = self._get_food_calories(food.food_id)
            result = FoodSearchResult(
                food_id=food.food_id,
                name=food.name,
                category=food.category,
                food_type=food.food_type,
                allergens=food.allergens,
                calories_per_serving=calories
            )
            results.append(result)
        
        return results

    def create_custom_food(
        self,
        name: str,
        serving_size: str,
        calories: float,
        carbohydrates_g: Optional[float] = None,
        protein_g: Optional[float] = None,
        fat_g: Optional[float] = None,
        fiber_g: Optional[float] = None
    ) -> FoodDetail:
        """
        Create a custom food entry with manual nutritional data.
        
        Args:
            name: Food name
            serving_size: Serving size description
            calories: Calories per serving
            carbohydrates_g: Carbohydrates in grams
            protein_g: Protein in grams
            fat_g: Fat in grams
            fiber_g: Fiber in grams
            
        Returns:
            Created food detail
        """
        # Create food entry
        food = Food(
            name=name,
            description=f"Custom entry: {serving_size}",
            category="Custom Foods",
            food_type="custom",
            allergens=None
        )
        
        self.db.add(food)
        self.db.flush()  # Get the food_id
        
        # Create nutrient entries
        # Note: Store per 100g for consistency with database foods
        nutrients_to_add = []
        
        # Energy (calories) - store per 100g
        energy_nutrient = self.db.query(Nutrient).filter(
            Nutrient.name.ilike('%energy%'),
            Nutrient.unit.ilike('KCAL')
        ).first()
        
        if energy_nutrient:
            food_nutrient = FoodNutrient(
                food_id=food.food_id,
                nutrient_id=energy_nutrient.nutrient_id,
                amount=calories,  # Store as-is, will be used directly
                per_unit="100g"  # Standard unit for consistency
            )
            nutrients_to_add.append(food_nutrient)
        
        # Carbohydrates
        if carbohydrates_g is not None and carbohydrates_g > 0:
            carb_nutrient = self.db.query(Nutrient).filter(
                Nutrient.name.ilike('%carbohydrate%'),
                Nutrient.unit.ilike('G')
            ).first()
            
            if carb_nutrient:
                food_nutrient = FoodNutrient(
                    food_id=food.food_id,
                    nutrient_id=carb_nutrient.nutrient_id,
                    amount=carbohydrates_g,
                    per_unit="100g"
                )
                nutrients_to_add.append(food_nutrient)
        
        # Protein
        if protein_g is not None and protein_g > 0:
            protein_nutrient = self.db.query(Nutrient).filter(
                Nutrient.name.ilike('%protein%'),
                Nutrient.unit.ilike('G')
            ).first()
            
            if protein_nutrient:
                food_nutrient = FoodNutrient(
                    food_id=food.food_id,
                    nutrient_id=protein_nutrient.nutrient_id,
                    amount=protein_g,
                    per_unit="100g"
                )
                nutrients_to_add.append(food_nutrient)
        
        # Fat
        if fat_g is not None and fat_g > 0:
            fat_nutrient = self.db.query(Nutrient).filter(
                Nutrient.name.ilike('%total lipid%'),
                Nutrient.unit.ilike('G')
            ).first()
            
            if not fat_nutrient:
                fat_nutrient = self.db.query(Nutrient).filter(
                    Nutrient.name.ilike('%fat%'),
                    Nutrient.unit.ilike('G')
                ).first()
            
            if fat_nutrient:
                food_nutrient = FoodNutrient(
                    food_id=food.food_id,
                    nutrient_id=fat_nutrient.nutrient_id,
                    amount=fat_g,
                    per_unit="100g"
                )
                nutrients_to_add.append(food_nutrient)
        
        # Fiber
        if fiber_g is not None and fiber_g > 0:
            fiber_nutrient = self.db.query(Nutrient).filter(
                Nutrient.name.ilike('%fiber%'),
                Nutrient.unit.ilike('G')
            ).first()
            
            if fiber_nutrient:
                food_nutrient = FoodNutrient(
                    food_id=food.food_id,
                    nutrient_id=fiber_nutrient.nutrient_id,
                    amount=fiber_g,
                    per_unit="100g"
                )
                nutrients_to_add.append(food_nutrient)
        
        # Add all nutrients
        for nutrient in nutrients_to_add:
            self.db.add(nutrient)
        
        self.db.commit()
        self.db.refresh(food)
        
        logger.info(f"Created custom food: {name} ({serving_size}) with {len(nutrients_to_add)} nutrients")
        
        # Return food detail
        return self.get_food_by_id(food.food_id)
