"""
Base imports for all models.
"""

from app.db.database import Base

# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.health_metrics import HealthMetrics
from app.models.prediction import Prediction
from app.models.food import Food
from app.models.nutrient import Nutrient
from app.models.food_nutrient import FoodNutrient
from app.models.food_entry import FoodEntry
from app.models.user_profile import UserProfile
from app.models.ml_model_metadata import MLModelMetadata