"""
Script to populate the food database from CSV files.

This script parses CSV files containing food, nutrient, and nutritional data,
validates the data, and populates the PostgreSQL database.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Set
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.db.database import SessionLocal, engine
from app.models import Food, Nutrient, FoodNutrient
from app.services.food_parser import FoodDataParser
from app.schemas.food_data import ParsedFood, ParsedNutrient, ParsedFoodNutrient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FoodDatabasePopulator:
    """Populates the food database from parsed CSV data."""
    
    def __init__(self, db: Session):
        """
        Initialize the populator.
        
        Args:
            db: Database session
        """
        self.db = db
        self.fdc_id_to_uuid: Dict[str, str] = {}
        self.nutrient_id_to_uuid: Dict[str, str] = {}
        self.duplicate_count = 0
        self.error_count = 0
    
    def _create_indexes(self) -> None:
        """Create database indexes for food search performance."""
        logger.info("Creating database indexes...")
        
        try:
            # Full-text search index on food name
            self.db.execute(text(
                """
                CREATE INDEX IF NOT EXISTS idx_foods_name_fts 
                ON foods USING gin(to_tsvector('english', name))
                """
            ))
            
            # Index on food category
            self.db.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_foods_category ON foods(category)"
            ))
            
            # Index on food allergens (GIN index for array)
            self.db.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_foods_allergens ON foods USING gin(allergens)"
            ))
            
            # Index on food_nutrients for food_id
            self.db.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_food_nutrients_food ON food_nutrients(food_id)"
            ))
            
            self.db.commit()
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            self.db.rollback()
    
    def populate_nutrients(self, nutrients: list[ParsedNutrient]) -> int:
        """
        Populate nutrients table.
        
        Args:
            nutrients: List of parsed nutrients
            
        Returns:
            Number of nutrients inserted
        """
        logger.info(f"Populating {len(nutrients)} nutrients...")
        inserted_count = 0
        
        for nutrient in nutrients:
            try:
                # Check if nutrient already exists
                existing = self.db.query(Nutrient).filter(
                    Nutrient.name == nutrient.name
                ).first()
                
                if existing:
                    self.duplicate_count += 1
                    self.nutrient_id_to_uuid[nutrient.nutrient_id] = str(existing.nutrient_id)
                    continue
                
                # Create new nutrient
                db_nutrient = Nutrient(
                    name=nutrient.name,
                    unit=nutrient.unit,
                    nutrient_type=nutrient.nutrient_type
                )
                
                self.db.add(db_nutrient)
                self.db.flush()  # Get the UUID
                
                # Map original ID to UUID
                self.nutrient_id_to_uuid[nutrient.nutrient_id] = str(db_nutrient.nutrient_id)
                inserted_count += 1
                
                if inserted_count % 100 == 0:
                    logger.info(f"Inserted {inserted_count} nutrients...")
                    self.db.commit()
                
            except IntegrityError as e:
                logger.warning(f"Duplicate nutrient: {nutrient.name}")
                self.db.rollback()
                self.duplicate_count += 1
                
                # Try to get existing nutrient
                existing = self.db.query(Nutrient).filter(
                    Nutrient.name == nutrient.name
                ).first()
                if existing:
                    self.nutrient_id_to_uuid[nutrient.nutrient_id] = str(existing.nutrient_id)
                
            except Exception as e:
                logger.error(f"Error inserting nutrient {nutrient.name}: {e}")
                self.db.rollback()
                self.error_count += 1
        
        self.db.commit()
        logger.info(f"Inserted {inserted_count} nutrients")
        return inserted_count
    
    def populate_foods(self, foods: list[ParsedFood]) -> int:
        """
        Populate foods table.
        
        Args:
            foods: List of parsed foods
            
        Returns:
            Number of foods inserted
        """
        logger.info(f"Populating {len(foods)} foods...")
        inserted_count = 0
        
        for food in foods:
            try:
                # Check if food already exists (by fdc_id stored in description)
                existing = self.db.query(Food).filter(
                    Food.name == food.name,
                    Food.category == food.category
                ).first()
                
                if existing:
                    self.duplicate_count += 1
                    self.fdc_id_to_uuid[food.fdc_id] = str(existing.food_id)
                    continue
                
                # Create new food
                db_food = Food(
                    name=food.name,
                    description=food.description,
                    category=food.category,
                    food_type=food.food_type,
                    allergens=food.allergens if food.allergens else None
                )
                
                self.db.add(db_food)
                self.db.flush()  # Get the UUID
                
                # Map original FDC ID to UUID
                self.fdc_id_to_uuid[food.fdc_id] = str(db_food.food_id)
                inserted_count += 1
                
                if inserted_count % 100 == 0:
                    logger.info(f"Inserted {inserted_count} foods...")
                    self.db.commit()
                
            except IntegrityError as e:
                logger.warning(f"Duplicate food: {food.name}")
                self.db.rollback()
                self.duplicate_count += 1
                
                # Try to get existing food
                existing = self.db.query(Food).filter(
                    Food.name == food.name,
                    Food.category == food.category
                ).first()
                if existing:
                    self.fdc_id_to_uuid[food.fdc_id] = str(existing.food_id)
                
            except Exception as e:
                logger.error(f"Error inserting food {food.name}: {e}")
                self.db.rollback()
                self.error_count += 1
        
        self.db.commit()
        logger.info(f"Inserted {inserted_count} foods")
        return inserted_count
    
    def populate_food_nutrients(
        self, 
        food_nutrients: list[ParsedFoodNutrient]
    ) -> int:
        """
        Populate food_nutrients junction table.
        
        Args:
            food_nutrients: List of parsed food-nutrient relationships
            
        Returns:
            Number of relationships inserted
        """
        logger.info(f"Populating {len(food_nutrients)} food-nutrient relationships...")
        inserted_count = 0
        skipped_count = 0
        
        for fn in food_nutrients:
            try:
                # Get UUIDs from mappings
                food_uuid = self.fdc_id_to_uuid.get(fn.fdc_id)
                nutrient_uuid = self.nutrient_id_to_uuid.get(fn.nutrient_id)
                
                if not food_uuid or not nutrient_uuid:
                    skipped_count += 1
                    continue
                
                # Check if relationship already exists
                existing = self.db.query(FoodNutrient).filter(
                    FoodNutrient.food_id == food_uuid,
                    FoodNutrient.nutrient_id == nutrient_uuid
                ).first()
                
                if existing:
                    self.duplicate_count += 1
                    continue
                
                # Create new food-nutrient relationship
                db_food_nutrient = FoodNutrient(
                    food_id=food_uuid,
                    nutrient_id=nutrient_uuid,
                    amount=fn.amount,
                    per_unit=fn.per_unit
                )
                
                self.db.add(db_food_nutrient)
                inserted_count += 1
                
                if inserted_count % 1000 == 0:
                    logger.info(f"Inserted {inserted_count} food-nutrient relationships...")
                    self.db.commit()
                
            except IntegrityError as e:
                logger.warning(
                    f"Duplicate food-nutrient: food={fn.fdc_id}, nutrient={fn.nutrient_id}"
                )
                self.db.rollback()
                self.duplicate_count += 1
                
            except Exception as e:
                logger.error(
                    f"Error inserting food-nutrient "
                    f"(food={fn.fdc_id}, nutrient={fn.nutrient_id}): {e}"
                )
                self.db.rollback()
                self.error_count += 1
        
        self.db.commit()
        logger.info(
            f"Inserted {inserted_count} food-nutrient relationships "
            f"(skipped {skipped_count} due to missing references)"
        )
        return inserted_count
    
    def populate_all(self, data_dir: Path = Path(".")) -> Dict[str, int]:
        """
        Parse CSV files and populate the database.
        
        Args:
            data_dir: Directory containing CSV files
            
        Returns:
            Dictionary with counts of inserted records
        """
        logger.info("Starting food database population...")
        
        # Parse CSV files
        parser = FoodDataParser(data_dir)
        result = parser.parse_all()
        
        if not result.success:
            logger.warning(
                f"CSV parsing completed with {len(result.errors)} errors"
            )
            for error in result.errors[:10]:  # Show first 10 errors
                logger.warning(
                    f"  {error.file_name} row {error.row_number}: {error.error_message}"
                )
        
        if not result.data:
            logger.error("No data parsed from CSV files")
            return {
                "nutrients": 0,
                "foods": 0,
                "food_nutrients": 0,
                "duplicates": 0,
                "errors": len(result.errors)
            }
        
        # Populate database
        nutrients_count = self.populate_nutrients(result.data.nutrients)
        foods_count = self.populate_foods(result.data.foods)
        food_nutrients_count = self.populate_food_nutrients(result.data.food_nutrients)
        
        # Create indexes
        self._create_indexes()
        
        stats = {
            "nutrients": nutrients_count,
            "foods": foods_count,
            "food_nutrients": food_nutrients_count,
            "duplicates": self.duplicate_count,
            "errors": self.error_count + len(result.errors)
        }
        
        logger.info("Food database population complete!")
        logger.info(f"Statistics: {stats}")
        
        return stats


def main():
    """Main entry point for the script."""
    logger.info("Food Database Population Script")
    logger.info("=" * 50)
    
    # Get data directory from command line or use current directory
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    logger.info(f"Data directory: {data_dir.absolute()}")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create populator and run
        populator = FoodDatabasePopulator(db)
        stats = populator.populate_all(data_dir)
        
        # Print summary
        logger.info("\n" + "=" * 50)
        logger.info("SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Nutrients inserted:           {stats['nutrients']}")
        logger.info(f"Foods inserted:               {stats['foods']}")
        logger.info(f"Food-Nutrient links inserted: {stats['food_nutrients']}")
        logger.info(f"Duplicates skipped:           {stats['duplicates']}")
        logger.info(f"Errors encountered:           {stats['errors']}")
        logger.info("=" * 50)
        
        if stats['errors'] > 0:
            logger.warning("Some errors occurred during population. Check logs above.")
            sys.exit(1)
        else:
            logger.info("Database population completed successfully!")
            sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
