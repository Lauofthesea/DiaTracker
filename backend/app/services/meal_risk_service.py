"""
Meal Risk Service - Predicts glucose response to meals using RF #1.
"""

from typing import Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import logging

from app.services.rf_model_manager import RFModelManager

logger = logging.getLogger(__name__)


class MealRiskService:
    """Service for meal-based glucose predictions."""
    
    def __init__(self, db: Session):
        self.db = db
        self.model_manager = RFModelManager()
    
    def predict_meal_risk(
        self,
        user_id: str,
        fasting_glucose: float,
        available_carbs_g: float,
        fat_g: float,
        protein_g: float,
        fiber_g: float,
        bmi: float,
        age: int,
        gender: int,
        food_entry_id: Optional[str] = None
    ) -> Dict:
        """
        Generate meal risk prediction.
        
        Args:
            user_id: User ID
            fasting_glucose: Fasting glucose level (mg/dL)
            available_carbs_g: Available carbohydrates in meal (g)
            fat_g: Fat content in meal (g)
            protein_g: Protein content in meal (g)
            fiber_g: Fiber content in meal (g)
            bmi: User's BMI
            age: User's age
            gender: User's gender (0=Male, 1=Female)
            food_entry_id: Optional food entry ID to link prediction
        
        Returns:
            Dictionary with prediction results
        """
        # Prepare features for glucose predictor
        features = {
            'fasting_glucose': float(fasting_glucose),
            'available_carbs_g': float(available_carbs_g),
            'fat_g': float(fat_g),
            'protein_g': float(protein_g),
            'fiber_g': float(fiber_g),
            'BMI': float(bmi),
            'age': int(age),
            'gender': int(gender)
        }
        
        logger.info(f"Predicting meal risk for user {user_id}")
        logger.debug(f"Features: {features}")
        
        # Predict glucose
        predicted_glucose, (lower, upper) = self.model_manager.predict_glucose(features)
        
        # Classify risk level
        risk_level = self._classify_meal_risk(predicted_glucose)
        
        # Generate explanation
        explanation = self._generate_explanation(predicted_glucose, risk_level)
        
        # Store prediction in database ONLY if linked to a food entry
        # (i.e., meal was actually confirmed, not just previewed)
        prediction_id = None
        if food_entry_id:
            prediction_id = self._store_prediction(
                user_id=user_id,
                features=features,
                predicted_glucose=predicted_glucose,
                confidence_lower=lower,
                confidence_upper=upper,
                risk_level=risk_level,
                food_entry_id=food_entry_id
            )
        
        return {
            'prediction_id': str(prediction_id) if prediction_id else None,
            'predicted_glucose_1hr': predicted_glucose,
            'confidence_interval': {
                'lower': lower,
                'upper': upper
            },
            'risk_level': risk_level,
            'risk_explanation': explanation,
            'model_version': '1.0.0-rf',
            'predicted_at': datetime.utcnow().isoformat()
        }
    
    def _classify_meal_risk(self, glucose: float) -> str:
        """
        Classify meal risk based on predicted glucose.
        
        Based on ADA 2024 guidelines:
        - Low: < 140 mg/dL (normal postprandial)
        - Mid: 140-199 mg/dL (prediabetic range)
        - High: ≥ 200 mg/dL (diabetic range)
        
        Args:
            glucose: Predicted 1-hour post-meal glucose (mg/dL)
        
        Returns:
            Risk level: "Low", "Mid", or "High"
        """
        if glucose < 140:
            return "Low"
        elif glucose < 200:
            return "Mid"
        else:
            return "High"
    
    def _generate_explanation(self, glucose: float, risk_level: str) -> str:
        """
        Generate human-readable risk explanation.
        
        Args:
            glucose: Predicted glucose level
            risk_level: Classified risk level
        
        Returns:
            Human-readable explanation string
        """
        explanations = {
            "Low": (
                f"This meal is predicted to keep your glucose at {glucose:.1f} mg/dL, "
                f"within normal postprandial range (<140 mg/dL). This is a healthy choice."
            ),
            "Mid": (
                f"This meal may elevate your glucose to {glucose:.1f} mg/dL, "
                f"approaching prediabetic range (140-200 mg/dL). Consider reducing portion size "
                f"or pairing with fiber-rich foods."
            ),
            "High": (
                f"⚠️ Warning: This meal may spike your glucose to {glucose:.1f} mg/dL, "
                f"which is in the diabetic range (≥200 mg/dL). Consider choosing a different meal "
                f"or significantly reducing portion size."
            )
        }
        return explanations[risk_level]
    
    def _store_prediction(
        self,
        user_id: str,
        features: Dict,
        predicted_glucose: float,
        confidence_lower: float,
        confidence_upper: float,
        risk_level: str,
        food_entry_id: Optional[str]
    ) -> uuid.UUID:
        """
        Store meal prediction in database.
        
        Args:
            user_id: User ID
            features: Feature dictionary used for prediction
            predicted_glucose: Predicted glucose value
            confidence_lower: Lower confidence bound
            confidence_upper: Upper confidence bound
            risk_level: Risk classification
            food_entry_id: Optional food entry ID
        
        Returns:
            UUID of created prediction
        """
        # Import here to avoid circular dependency
        from app.models.meal_prediction import MealPrediction
        
        prediction = MealPrediction(
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            food_entry_id=uuid.UUID(food_entry_id) if food_entry_id and isinstance(food_entry_id, str) else food_entry_id,
            fasting_glucose=features['fasting_glucose'],
            available_carbs_g=features['available_carbs_g'],
            fat_g=features['fat_g'],
            protein_g=features['protein_g'],
            fiber_g=features['fiber_g'],
            bmi=features['BMI'],
            age=features['age'],
            gender=features['gender'],
            predicted_glucose_1hr=predicted_glucose,
            confidence_lower=confidence_lower,
            confidence_upper=confidence_upper,
            risk_level=risk_level,
            model_version='1.0.0-rf'
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        logger.info(f"Stored meal prediction {prediction.prediction_id} for user {user_id}")
        
        return prediction.prediction_id
    
    def get_meal_history(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        risk_level: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        Retrieve meal prediction history for a user.
        
        Args:
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            risk_level: Optional risk level filter ("Low", "Mid", "High")
            page: Page number (1-indexed)
            page_size: Number of results per page
        
        Returns:
            Dictionary with predictions and pagination info
        """
        from app.models.meal_prediction import MealPrediction
        
        # Build query
        query = self.db.query(MealPrediction).filter(
            MealPrediction.user_id == uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        )
        
        # Apply filters
        if start_date:
            query = query.filter(MealPrediction.predicted_at >= start_date)
        if end_date:
            query = query.filter(MealPrediction.predicted_at <= end_date)
        if risk_level:
            query = query.filter(MealPrediction.risk_level == risk_level)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        predictions = query.order_by(
            MealPrediction.predicted_at.desc()
        ).offset(offset).limit(page_size).all()
        
        # Format results
        results = []
        for pred in predictions:
            results.append({
                'prediction_id': str(pred.prediction_id),
                'predicted_glucose_1hr': float(pred.predicted_glucose_1hr),
                'risk_level': pred.risk_level,
                'meal_composition': {
                    'available_carbs_g': float(pred.available_carbs_g),
                    'fat_g': float(pred.fat_g),
                    'protein_g': float(pred.protein_g),
                    'fiber_g': float(pred.fiber_g)
                },
                'confidence_interval': {
                    'lower': float(pred.confidence_lower) if pred.confidence_lower else None,
                    'upper': float(pred.confidence_upper) if pred.confidence_upper else None
                },
                'predicted_at': pred.predicted_at.isoformat(),
                'food_entry_id': str(pred.food_entry_id) if pred.food_entry_id else None
            })
        
        return {
            'predictions': results,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }
