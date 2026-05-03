"""
Diabetes prediction service for real-time ML predictions.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.ml_model_metadata import MLModelMetadata
from app.models.prediction import Prediction
from app.models.health_metrics import HealthMetrics
from app.schemas.health_metrics import SymptomsEncoded
from app.core.config import settings


class DiabetesPredictionService:
    """Service for diabetes prediction using trained ML models."""
    
    def __init__(self, db: Session, model_path: Optional[str] = None):
        """
        Initialize diabetes prediction service.
        
        Args:
            db: Database session
            model_path: Optional path to specific model file. If None, loads active model.
        """
        self.db = db
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_list = None
        self.model_version = None
        self.model_metadata = None
        
        # Load model
        if model_path:
            self._load_model_from_path(model_path)
        else:
            self._load_active_model()
    
    def _load_active_model(self):
        """Load the currently active model from database."""
        # Get active model metadata
        active_model = self.db.query(MLModelMetadata).filter(
            MLModelMetadata.is_active == True
        ).first()
        
        if active_model:
            # Check if the model file actually exists
            if not os.path.exists(active_model.model_path):
                print(f"Warning: Active model file not found at {active_model.model_path}")
                print("Falling back to default model path...")
                # Deactivate this broken model record
                active_model.is_active = False
                self.db.commit()
                active_model = None
        
        if not active_model:
            # Fallback: Load model directly from default path
            print("Warning: No active model found in database. Loading from default path...")
            
            # Get the absolute path to the ml_models directory
            # __file__ is in backend/app/services/diabetes_prediction_service.py
            # We need to go up to backend/ and then into ml_models/
            service_dir = os.path.dirname(os.path.abspath(__file__))  # backend/app/services
            app_dir = os.path.dirname(service_dir)  # backend/app
            backend_dir = os.path.dirname(app_dir)  # backend
            default_model_path = os.path.join(backend_dir, "ml_models", "diabetes_model.pkl")
            
            print(f"Looking for model at: {default_model_path}")
            
            if not os.path.exists(default_model_path):
                raise ValueError(
                    f"No active model found in database and default model file not found at {default_model_path}. "
                    "Please run 'python scripts/register_model.py' to register the model."
                )
            
            self.model_version = "1.0.0"
            self._load_model_from_path(default_model_path)
            return
        
        self.model_metadata = active_model
        self.model_version = active_model.version
        
        # Load model from disk
        self._load_model_from_path(active_model.model_path)
    
    def _load_model_from_path(self, model_path: str):
        """
        Load model, scaler, and label encoder from disk.
        
        Args:
            model_path: Path to model file
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load model bundle
        model_bundle = joblib.load(model_path)
        
        self.model = model_bundle['model']
        self.scaler = model_bundle['scaler']
        self.label_encoder = model_bundle['label_encoder']
        self.feature_list = model_bundle['feature_list']
        
        print(f"Model loaded successfully from: {model_path}")
        print(f"Features: {self.feature_list}")
    
    def preprocess_features(self, health_metrics: HealthMetrics) -> np.ndarray:
        """
        Preprocess health metrics into model input features.
        
        Args:
            health_metrics: HealthMetrics object with user health data
        
        Returns:
            Preprocessed feature array ready for model prediction
        """
        # Encode symptoms
        symptoms_encoded = SymptomsEncoded.from_symptoms_list(
            health_metrics.symptoms if health_metrics.symptoms else []
        )
        
        # Map our health metrics to the model's expected features
        # The model was trained on the Pima Indians Diabetes dataset with these features:
        # Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
        
        features = {
            'Pregnancies': 0,  # Default to 0 (we don't collect this)
            'Glucose': float(health_metrics.blood_sugar_mgdl),  # Map blood_sugar to Glucose
            'BloodPressure': 70,  # Default average (we don't collect this)
            'SkinThickness': 20,  # Default average (we don't collect this)
            'Insulin': 80,  # Default average (we don't collect this)
            'BMI': float(health_metrics.bmi),
            'DiabetesPedigreeFunction': 0.5,  # Default average (we don't collect this)
            'Age': int(health_metrics.age),
        }
        
        # Create DataFrame with features in correct order
        feature_df = pd.DataFrame([features])
        
        # Select only features used by the model (in correct order)
        if self.feature_list:
            # Ensure all required features are present
            missing_features = set(self.feature_list) - set(feature_df.columns)
            if missing_features:
                raise ValueError(f"Missing required features: {missing_features}")
            
            feature_df = feature_df[self.feature_list]
        
        # Normalize features using the scaler from training
        features_scaled = self.scaler.transform(feature_df)
        
        return features_scaled
    
    def predict(
        self, 
        health_metrics: HealthMetrics
    ) -> Tuple[str, float, Dict[str, float]]:
        """
        Generate diabetes prediction from health metrics.
        
        Args:
            health_metrics: HealthMetrics object with user health data
        
        Returns:
            Tuple of (classification, confidence, probabilities)
            - classification: str ('No Diabetes', 'Has Diabetes')
            - confidence: float (0-1) - highest probability
            - probabilities: dict {class: probability}
        """
        if self.model is None:
            raise ValueError("Model not loaded. Cannot make predictions.")
        
        # Preprocess features
        features = self.preprocess_features(health_metrics)
        
        # Get prediction probabilities
        probabilities_array = self.model.predict_proba(features)[0]
        
        # Get class prediction
        prediction_encoded = self.model.predict(features)[0]
        
        # Decode prediction to class name
        if self.label_encoder:
            # Multi-class classification with label encoder
            classification = self.label_encoder.inverse_transform([prediction_encoded])[0]
            class_names = self.label_encoder.classes_
        else:
            # Binary classification (0 = No Diabetes, 1 = Has Diabetes)
            class_names = ['No Diabetes', 'Has Diabetes']
            classification = class_names[prediction_encoded]
        
        # Create probability dictionary
        probabilities = {
            class_name: float(prob) 
            for class_name, prob in zip(class_names, probabilities_array)
        }
        
        # Confidence is the highest probability
        confidence = float(max(probabilities_array))
        
        return classification, confidence, probabilities
    
    def create_prediction_record(
        self,
        user_id: str,
        metric_id: str,
        classification: str,
        confidence: float,
        probabilities: Dict[str, float]
    ) -> Prediction:
        """
        Create and store prediction record in database.
        
        Args:
            user_id: User ID
            metric_id: Health metrics ID
            classification: Predicted diabetes type
            confidence: Confidence score
            probabilities: Probability distribution
        
        Returns:
            Created Prediction object
        """
        prediction = Prediction(
            user_id=user_id,
            metric_id=metric_id,
            model_version=self.model_version,
            classification=classification,
            confidence=confidence,
            probabilities=probabilities
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        return prediction
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model metadata
        """
        if self.model_metadata:
            return {
                'model_name': self.model_metadata.model_name,
                'model_type': self.model_metadata.model_type,
                'version': self.model_metadata.version,
                'accuracy': float(self.model_metadata.accuracy) if self.model_metadata.accuracy else None,
                'precision_type1': float(self.model_metadata.precision_type1) if self.model_metadata.precision_type1 else None,
                'precision_type2': float(self.model_metadata.precision_type2) if self.model_metadata.precision_type2 else None,
                'recall': float(self.model_metadata.recall) if self.model_metadata.recall else None,
                'f1_score': float(self.model_metadata.f1_score) if self.model_metadata.f1_score else None,
                'training_date': self.model_metadata.training_date.isoformat() if self.model_metadata.training_date else None,
                'feature_list': self.feature_list
            }
        else:
            return {
                'model_name': 'Unknown',
                'model_type': 'Unknown',
                'version': self.model_version,
                'feature_list': self.feature_list
            }
    
    def log_prediction(
        self,
        prediction: Prediction,
        health_metrics: HealthMetrics,
        ground_truth: Optional[str] = None
    ):
        """
        Log prediction for performance monitoring.
        
        Args:
            prediction: Prediction object
            health_metrics: Health metrics used for prediction
            ground_truth: Actual diagnosis (if available)
        """
        from app.services.model_performance_service import ModelPerformanceService
        
        # Use performance monitoring service for detailed logging
        performance_service = ModelPerformanceService(self.db)
        performance_service.log_prediction(prediction, health_metrics, ground_truth)
        
        # Also log to console for debugging
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'prediction_id': str(prediction.prediction_id),
            'user_id': str(prediction.user_id),
            'model_version': prediction.model_version,
            'classification': prediction.classification,
            'confidence': float(prediction.confidence),
            'input_features': {
                'weight_kg': float(health_metrics.weight_kg),
                'blood_sugar_mgdl': float(health_metrics.blood_sugar_mgdl),
                'age': health_metrics.age,
                'bmi': float(health_metrics.bmi),
                'symptoms': health_metrics.symptoms
            }
        }
        
        print(f"Prediction logged: {log_entry}")
    
    def calculate_rolling_accuracy(self, window_size: int = 1000) -> Optional[float]:
        """
        Calculate rolling accuracy over recent predictions.
        
        Args:
            window_size: Number of recent predictions to consider
        
        Returns:
            Rolling accuracy or None if insufficient data
        """
        # Get recent predictions
        recent_predictions = self.db.query(Prediction).order_by(
            Prediction.predicted_at.desc()
        ).limit(window_size).all()
        
        if len(recent_predictions) < 100:
            # Not enough data for meaningful accuracy calculation
            return None
        
        # In a real system, we would need ground truth labels to calculate accuracy
        # For now, we'll return None as this requires actual validation data
        # This would be implemented with a separate validation dataset or user feedback
        return None
    
    def check_model_performance(self) -> Dict:
        """
        Check model performance metrics and generate alerts if needed.
        
        Returns:
            Dictionary with performance status and alerts
        """
        rolling_accuracy = self.calculate_rolling_accuracy()
        
        alerts = []
        
        # Check if accuracy has dropped below threshold
        if rolling_accuracy is not None and rolling_accuracy < 0.80:
            alerts.append({
                'type': 'LOW_ACCURACY',
                'message': f'Model accuracy has dropped to {rolling_accuracy:.2%}. Retraining recommended.',
                'severity': 'HIGH',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check model age
        if self.model_metadata:
            days_since_training = (datetime.utcnow() - self.model_metadata.training_date).days
            if days_since_training > 90:
                alerts.append({
                    'type': 'MODEL_AGE',
                    'message': f'Model is {days_since_training} days old. Consider retraining with recent data.',
                    'severity': 'MEDIUM',
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        return {
            'rolling_accuracy': rolling_accuracy,
            'model_version': self.model_version,
            'alerts': alerts,
            'status': 'HEALTHY' if len(alerts) == 0 else 'NEEDS_ATTENTION'
        }
