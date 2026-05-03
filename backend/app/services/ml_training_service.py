"""
ML model training service for diabetes prediction.
"""

import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sqlalchemy.orm import Session

from app.models.ml_model_metadata import MLModelMetadata
from app.core.config import settings


class MLTrainingService:
    """Service for training and evaluating ML models."""
    
    def __init__(self, db: Session):
        """Initialize ML training service."""
        self.db = db
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.models = {
            'Logistic Regression': LogisticRegression(
                max_iter=1000,
                random_state=42,
                solver='lbfgs'
            ),
            'Random Forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'Neural Network': MLPClassifier(
                hidden_layer_sizes=(64, 32, 16),
                max_iter=1000,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            )
        }
        
        # Ensure model directory exists
        os.makedirs(settings.MODEL_PATH, exist_ok=True)
    
    def preprocess_data(
        self, 
        X: pd.DataFrame, 
        y: Optional[pd.Series] = None,
        fit_scaler: bool = False,
        fit_label_encoder: bool = False
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Preprocess features and labels for ML model.
        
        Args:
            X: Feature dataframe
            y: Target series (optional)
            fit_scaler: Whether to fit the scaler (True for training, False for prediction)
            fit_label_encoder: Whether to fit the label encoder (True for training, False for prediction)
        
        Returns:
            Tuple of (preprocessed features, preprocessed target)
        """
        # Handle missing values - use median imputation
        X_filled = X.fillna(X.median())
        
        # Detect and log outliers (beyond 3 standard deviations)
        for column in X_filled.select_dtypes(include=[np.number]).columns:
            mean = X_filled[column].mean()
            std = X_filled[column].std()
            outliers = X_filled[(X_filled[column] < mean - 3*std) | (X_filled[column] > mean + 3*std)]
            if len(outliers) > 0:
                print(f"Warning: {len(outliers)} outliers detected in {column}")
        
        # Normalize numerical features
        if fit_scaler:
            X_scaled = self.scaler.fit_transform(X_filled)
        else:
            X_scaled = self.scaler.transform(X_filled)
        
        # Validate statistical properties are preserved (correlation)
        if fit_scaler and X_filled.shape[1] > 1:
            original_corr = np.corrcoef(X_filled.T)
            scaled_corr = np.corrcoef(X_scaled.T)
            correlation_preserved = np.corrcoef(original_corr.flatten(), scaled_corr.flatten())[0, 1]
            print(f"Statistical property preservation (correlation): {correlation_preserved:.4f}")
        
        # Encode labels if provided
        y_encoded = None
        if y is not None:
            if fit_label_encoder:
                y_encoded = self.label_encoder.fit_transform(y)
            else:
                y_encoded = self.label_encoder.transform(y)
        
        return X_scaled, y_encoded
    
    def split_data(
        self, 
        X: np.ndarray, 
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Split data into training (70%), validation (15%), and test (15%) sets.
        
        Args:
            X: Feature array
            y: Target array
        
        Returns:
            Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        # First split: 70% train, 30% temp
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.30, random_state=42, stratify=y
        )
        
        # Second split: 15% validation, 15% test (50% of temp)
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
        )
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def train_model(
        self, 
        model_name: str, 
        X_train: np.ndarray, 
        y_train: np.ndarray
    ) -> object:
        """
        Train a specific model.
        
        Args:
            model_name: Name of the model to train
            X_train: Training features
            y_train: Training labels
        
        Returns:
            Trained model
        """
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        model = self.models[model_name]
        print(f"Training {model_name}...")
        model.fit(X_train, y_train)
        print(f"{model_name} training complete.")
        
        return model
    
    def evaluate_model(
        self, 
        model: object, 
        X: np.ndarray, 
        y: np.ndarray,
        dataset_name: str = "test"
    ) -> Dict[str, float]:
        """
        Evaluate model performance.
        
        Args:
            model: Trained model
            X: Feature array
            y: True labels
            dataset_name: Name of dataset being evaluated
        
        Returns:
            Dictionary of evaluation metrics
        """
        y_pred = model.predict(X)
        
        # Calculate metrics
        accuracy = accuracy_score(y, y_pred)
        
        # For multi-class, use weighted average
        precision = precision_score(y, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y, y_pred, average='weighted', zero_division=0)
        
        # Calculate per-class precision for Type 1 and Type 2
        precision_per_class = precision_score(y, y_pred, average=None, zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y, y_pred)
        
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'confusion_matrix': cm.tolist(),
            'precision_per_class': precision_per_class.tolist()
        }
        
        print(f"\n{dataset_name.capitalize()} Set Metrics:")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1-Score: {f1:.4f}")
        print(f"  Confusion Matrix:\n{cm}")
        
        return metrics
    
    def save_model(
        self, 
        model: object, 
        model_name: str, 
        version: str,
        feature_list: List[str],
        metrics: Dict[str, float]
    ) -> str:
        """
        Save trained model and metadata to disk and database.
        
        Args:
            model: Trained model
            model_name: Name of the model
            version: Model version string
            feature_list: List of feature names
            metrics: Evaluation metrics
        
        Returns:
            Path to saved model
        """
        # Save model file
        model_filename = f"{model_name.replace(' ', '_').lower()}_{version}.joblib"
        model_path = os.path.join(settings.MODEL_PATH, model_filename)
        
        # Save model, scaler, and label encoder together
        joblib.dump({
            'model': model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_list': feature_list
        }, model_path)
        
        print(f"Model saved to: {model_path}")
        
        # Save metadata to database
        precision_type1 = metrics.get('precision_per_class', [0, 0, 0])[0] if len(metrics.get('precision_per_class', [])) > 0 else 0
        precision_type2 = metrics.get('precision_per_class', [0, 0, 0])[1] if len(metrics.get('precision_per_class', [])) > 1 else 0
        
        metadata = MLModelMetadata(
            model_name=model_name,
            model_type=model_name,
            version=version,
            accuracy=metrics['accuracy'],
            precision_type1=precision_type1,
            precision_type2=precision_type2,
            recall=metrics['recall'],
            f1_score=metrics['f1_score'],
            training_date=datetime.utcnow(),
            is_active=False,  # Will be set to True if best model
            model_path=model_path,
            feature_list=feature_list
        )
        
        self.db.add(metadata)
        self.db.commit()
        
        return model_path
    
    def select_best_model(
        self, 
        model_results: Dict[str, Dict]
    ) -> Tuple[str, object, Dict]:
        """
        Select the best performing model based on accuracy.
        
        Args:
            model_results: Dictionary mapping model names to (model, metrics) tuples
        
        Returns:
            Tuple of (best_model_name, best_model, best_metrics)
        """
        best_model_name = None
        best_accuracy = 0.0
        best_model = None
        best_metrics = None
        
        print("\n" + "="*50)
        print("Model Comparison:")
        print("="*50)
        
        for model_name, (model, metrics) in model_results.items():
            accuracy = metrics['accuracy']
            print(f"{model_name}: Accuracy = {accuracy:.4f}")
            
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_model_name = model_name
                best_model = model
                best_metrics = metrics
        
        print("="*50)
        print(f"Best Model: {best_model_name} (Accuracy: {best_accuracy:.4f})")
        print("="*50)
        
        return best_model_name, best_model, best_metrics
    
    def set_active_model(self, version: str):
        """
        Set a model version as active.
        
        Args:
            version: Model version to activate
        """
        # Deactivate all models
        self.db.query(MLModelMetadata).update({'is_active': False})
        
        # Activate the specified version
        model = self.db.query(MLModelMetadata).filter(
            MLModelMetadata.version == version
        ).first()
        
        if model:
            model.is_active = True
            self.db.commit()
            print(f"Model version {version} set as active.")
        else:
            print(f"Warning: Model version {version} not found.")
    
    def train_all_models(
        self, 
        X: pd.DataFrame, 
        y: pd.Series,
        version: str = None
    ) -> Dict[str, Tuple[object, Dict]]:
        """
        Train all model types and return results.
        
        Args:
            X: Feature dataframe
            y: Target series
            version: Model version string (default: timestamp)
        
        Returns:
            Dictionary mapping model names to (model, metrics) tuples
        """
        if version is None:
            version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        print("="*50)
        print("Starting ML Model Training Pipeline")
        print("="*50)
        
        # Preprocess data
        print("\nPreprocessing data...")
        X_processed, y_processed = self.preprocess_data(X, y, fit_scaler=True, fit_label_encoder=True)
        
        # Split data
        print("Splitting data (70% train, 15% validation, 15% test)...")
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(
            X_processed, y_processed
        )
        
        print(f"Training set size: {len(X_train)}")
        print(f"Validation set size: {len(X_val)}")
        print(f"Test set size: {len(X_test)}")
        
        # Train and evaluate all models
        model_results = {}
        feature_list = X.columns.tolist()
        
        for model_name in self.models.keys():
            print(f"\n{'='*50}")
            print(f"Training {model_name}")
            print(f"{'='*50}")
            
            # Train model
            model = self.train_model(model_name, X_train, y_train)
            
            # Evaluate on validation set
            val_metrics = self.evaluate_model(model, X_val, y_val, "validation")
            
            # Evaluate on test set
            test_metrics = self.evaluate_model(model, X_test, y_test, "test")
            
            # Save model
            self.save_model(model, model_name, version, feature_list, test_metrics)
            
            # Store results (using test metrics for comparison)
            model_results[model_name] = (model, test_metrics)
        
        # Select best model
        best_model_name, best_model, best_metrics = self.select_best_model(model_results)
        
        # Set best model as active
        self.set_active_model(version)
        
        print("\n" + "="*50)
        print("Training Pipeline Complete")
        print("="*50)
        
        return model_results
