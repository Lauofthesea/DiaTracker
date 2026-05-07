"""
Random Forest Model Manager - Singleton service for managing RF models.
"""

import os
import joblib
import numpy as np
from typing import Dict, Tuple, Optional, List
from threading import Lock
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RFModelManager:
    """Singleton manager for Random Forest models."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.glucose_predictor = None
        self.risk_classifier = None
        self.glucose_features = None
        self.risk_features = None
        self.model_metadata = {}
        self._initialized = True
        
        # Load models on initialization
        try:
            self._load_models()
            logger.info("RF Model Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RF Model Manager: {str(e)}")
            raise
    
    def _load_models(self):
        """Load both RF models from disk."""
        # Get the absolute path to the ml_models directory
        # __file__ is in backend/app/services/rf_model_manager.py
        service_dir = os.path.dirname(os.path.abspath(__file__))  # backend/app/services
        app_dir = os.path.dirname(service_dir)  # backend/app
        backend_dir = os.path.dirname(app_dir)  # backend
        base_path = os.path.join(backend_dir, 'ml_models')
        
        # Load Glucose Predictor (RF #1)
        glucose_path = os.path.join(base_path, 'glucose_predictor_rf.pkl')
        if not os.path.exists(glucose_path):
            raise FileNotFoundError(f"Glucose predictor model not found at {glucose_path}")
        
        logger.info(f"Loading glucose predictor from {glucose_path}")
        self.glucose_predictor = joblib.load(glucose_path)
        
        # Load Risk Classifier (RF #2)
        risk_path = os.path.join(base_path, 'risk_classifier_rf.pkl')
        if not os.path.exists(risk_path):
            raise FileNotFoundError(f"Risk classifier model not found at {risk_path}")
        
        logger.info(f"Loading risk classifier from {risk_path}")
        self.risk_classifier = joblib.load(risk_path)
        
        # Load feature lists
        glucose_features_path = os.path.join(base_path, 'glucose_predictor_features.txt')
        if not os.path.exists(glucose_features_path):
            raise FileNotFoundError(f"Glucose predictor features not found at {glucose_features_path}")
        
        with open(glucose_features_path, 'r') as f:
            self.glucose_features = [line.strip() for line in f if line.strip()]
        
        risk_features_path = os.path.join(base_path, 'risk_classifier_features.txt')
        if not os.path.exists(risk_features_path):
            raise FileNotFoundError(f"Risk classifier features not found at {risk_features_path}")
        
        with open(risk_features_path, 'r') as f:
            self.risk_features = [line.strip() for line in f if line.strip()]
        
        # Store metadata
        self.model_metadata = {
            'glucose_predictor': {
                'version': '1.0.0-rf',
                'loaded_at': datetime.utcnow(),
                'features': self.glucose_features,
                'n_features': len(self.glucose_features)
            },
            'risk_classifier': {
                'version': '2.0.0-rf',
                'loaded_at': datetime.utcnow(),
                'features': self.risk_features,
                'n_features': len(self.risk_features)
            }
        }
        
        logger.info(f"Glucose predictor features ({len(self.glucose_features)}): {self.glucose_features}")
        logger.info(f"Risk classifier features ({len(self.risk_features)}): {self.risk_features}")
    
    def predict_glucose(
        self, 
        features: Dict[str, float]
    ) -> Tuple[float, Tuple[float, float]]:
        """
        Predict 1-hour post-meal glucose.
        
        Args:
            features: Dict with keys matching glucose_features
                Expected keys: fasting_glucose, available_carbs_g, fat_g, 
                              protein_g, fiber_g, BMI, age, gender (0=Male, 1=Female)
        
        Returns:
            (predicted_glucose, (lower_bound, upper_bound))
        
        Raises:
            ValueError: If required features are missing
        """
        if self.glucose_predictor is None:
            raise RuntimeError("Glucose predictor model not loaded")
        
        # Validate features
        self._validate_features(features, self.glucose_features, "glucose predictor")
        
        # Create feature array in correct order
        X = np.array([[features[f] for f in self.glucose_features]])
        
        # Predict
        prediction = self.glucose_predictor.predict(X)[0]
        
        # Calculate confidence interval using prediction variance from trees
        # For RF, we can use the standard deviation of predictions from individual trees
        predictions_per_tree = np.array([
            tree.predict(X)[0] 
            for tree in self.glucose_predictor.estimators_
        ])
        std_dev = np.std(predictions_per_tree)
        
        # 95% confidence interval (approximately ±2 standard deviations)
        lower = max(0, prediction - 2 * std_dev)  # Glucose can't be negative
        upper = prediction + 2 * std_dev
        
        logger.debug(f"Glucose prediction: {prediction:.2f} mg/dL (CI: {lower:.2f}-{upper:.2f})")
        
        return float(prediction), (float(lower), float(upper))
    
    def predict_risk(
        self, 
        features: Dict[str, float]
    ) -> Tuple[str, float, Dict[str, float]]:
        """
        Predict diabetes risk classification.
        
        Args:
            features: Dict with keys matching risk_features
                Expected keys: fasting_glucose, BMI, age, gender (0=Male, 1=Female)
        
        Returns:
            (classification, confidence, probabilities)
            - classification: "Low", "Mid", or "High"
            - confidence: float (0-1) - highest probability
            - probabilities: dict mapping class names to probabilities
        
        Raises:
            ValueError: If required features are missing
        """
        if self.risk_classifier is None:
            raise RuntimeError("Risk classifier model not loaded")
        
        # Validate features
        self._validate_features(features, self.risk_features, "risk classifier")
        
        # Create feature array in correct order
        X = np.array([[features[f] for f in self.risk_features]])
        
        # Predict
        prediction = self.risk_classifier.predict(X)[0]
        probabilities = self.risk_classifier.predict_proba(X)[0]
        
        # Get class names (these are numeric: 0, 1, 2)
        classes = self.risk_classifier.classes_
        
        # Map numeric predictions to text labels
        # 0 = Low, 1 = Mid, 2 = High (based on training script)
        label_map = {0: 'Low', 1: 'Mid', 2: 'High', '0': 'Low', '1': 'Mid', '2': 'High'}
        classification = label_map.get(prediction, str(prediction))
        
        # Create probability dict with text labels
        prob_dict = {}
        for cls, prob in zip(classes, probabilities):
            text_label = label_map.get(cls, str(cls))
            prob_dict[text_label] = float(prob)
        
        confidence = float(max(probabilities))
        
        logger.debug(f"Risk prediction: {classification} (confidence: {confidence:.2%})")
        logger.debug(f"Probabilities: {prob_dict}")
        
        return classification, confidence, prob_dict
    
    def _validate_features(
        self, 
        features: Dict[str, float], 
        expected_features: List[str],
        model_name: str
    ):
        """
        Validate that all required features are present.
        
        Args:
            features: Feature dictionary to validate
            expected_features: List of required feature names
            model_name: Name of the model (for error messages)
        
        Raises:
            ValueError: If required features are missing
        """
        missing = set(expected_features) - set(features.keys())
        if missing:
            raise ValueError(
                f"Missing required features for {model_name}: {missing}. "
                f"Expected features: {expected_features}"
            )
        
        # Validate feature values are numeric
        for feature_name in expected_features:
            value = features[feature_name]
            if not isinstance(value, (int, float, np.number)):
                raise ValueError(
                    f"Feature '{feature_name}' must be numeric, got {type(value)}"
                )
    
    def get_model_info(self) -> Dict:
        """
        Get information about loaded models.
        
        Returns:
            Dictionary with model metadata including versions, features, and load times
        """
        return {
            'glucose_predictor': {
                'version': self.model_metadata['glucose_predictor']['version'],
                'loaded_at': self.model_metadata['glucose_predictor']['loaded_at'].isoformat(),
                'features': self.model_metadata['glucose_predictor']['features'],
                'n_features': self.model_metadata['glucose_predictor']['n_features'],
                'status': 'loaded' if self.glucose_predictor is not None else 'not_loaded'
            },
            'risk_classifier': {
                'version': self.model_metadata['risk_classifier']['version'],
                'loaded_at': self.model_metadata['risk_classifier']['loaded_at'].isoformat(),
                'features': self.model_metadata['risk_classifier']['features'],
                'n_features': self.model_metadata['risk_classifier']['n_features'],
                'status': 'loaded' if self.risk_classifier is not None else 'not_loaded'
            }
        }
    
    def validate_model_health(self) -> Dict[str, bool]:
        """
        Check if models are loaded and healthy.
        
        Returns:
            Dictionary with health status for each model
        """
        return {
            'glucose_predictor_loaded': self.glucose_predictor is not None,
            'risk_classifier_loaded': self.risk_classifier is not None,
            'all_models_healthy': (
                self.glucose_predictor is not None and 
                self.risk_classifier is not None
            )
        }
