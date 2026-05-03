"""
Train diabetes prediction model using the Pima Indians Diabetes Dataset.

This script:
1. Loads the preprocessed diabetes datasets from Datasets/ folder
2. Trains a Random Forest classifier
3. Evaluates model performance
4. Saves the trained model with metadata
5. Registers the model in the database

Usage:
    python -m app.ml.train_diabetes_model
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.db.database import SessionLocal
from app.models.ml_model_metadata import MLModelMetadata


class DiabetesModelTrainer:
    """Trainer for diabetes prediction model using Pima Indians dataset."""
    
    def __init__(self, datasets_dir: str = "Datasets"):
        """
        Initialize the trainer.
        
        Args:
            datasets_dir: Path to the datasets directory
        """
        self.datasets_dir = Path(datasets_dir)
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.metrics = {}
        
        # Model configuration
        self.model_name = "diabetes_rf_classifier"
        self.model_type = "RandomForest"
        self.version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def load_datasets(self):
        """Load training, validation, and test datasets."""
        print("Loading datasets...")
        
        # Load training data
        self.X_train = pd.read_csv(self.datasets_dir / "diabetes_X_train.csv")
        self.y_train = pd.read_csv(self.datasets_dir / "diabetes_y_train.csv")["Outcome"]
        
        # Load validation data
        self.X_val = pd.read_csv(self.datasets_dir / "diabetes_X_val.csv")
        self.y_val = pd.read_csv(self.datasets_dir / "diabetes_y_val.csv")["Outcome"]
        
        # Load test data
        self.X_test = pd.read_csv(self.datasets_dir / "diabetes_X_test.csv")
        self.y_test = pd.read_csv(self.datasets_dir / "diabetes_y_test.csv")["Outcome"]
        
        # Load scaler
        with open(self.datasets_dir / "diabetes_scaler.pkl", "rb") as f:
            self.scaler = joblib.load(f)
        
        # Load feature names
        with open(self.datasets_dir / "diabetes_feature_names.txt", "r") as f:
            self.feature_names = [line.strip() for line in f.readlines()]
        
        print(f"✓ Training samples: {len(self.X_train)}")
        print(f"✓ Validation samples: {len(self.X_val)}")
        print(f"✓ Test samples: {len(self.X_test)}")
        print(f"✓ Features: {self.feature_names}")
        print(f"✓ Class distribution (train): {dict(self.y_train.value_counts())}")
        
    def train_model(self):
        """Train the Random Forest classifier."""
        print("\nTraining Random Forest model...")
        
        # Initialize model with optimized hyperparameters
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=4,
            max_features='sqrt',
            class_weight='balanced',  # Handle class imbalance
            random_state=42,
            n_jobs=-1
        )
        
        # Train model
        self.model.fit(self.X_train, self.y_train)
        
        print("✓ Model training completed")
        
    def evaluate_model(self):
        """Evaluate model on validation and test sets."""
        print("\nEvaluating model...")
        
        # Validation set evaluation
        y_val_pred = self.model.predict(self.X_val)
        y_val_proba = self.model.predict_proba(self.X_val)
        
        val_accuracy = accuracy_score(self.y_val, y_val_pred)
        val_precision = precision_score(self.y_val, y_val_pred, average='weighted')
        val_recall = recall_score(self.y_val, y_val_pred, average='weighted')
        val_f1 = f1_score(self.y_val, y_val_pred, average='weighted')
        
        try:
            val_roc_auc = roc_auc_score(self.y_val, y_val_proba[:, 1])
        except:
            val_roc_auc = 0.0
        
        print("\n=== Validation Set Performance ===")
        print(f"Accuracy:  {val_accuracy:.4f}")
        print(f"Precision: {val_precision:.4f}")
        print(f"Recall:    {val_recall:.4f}")
        print(f"F1-Score:  {val_f1:.4f}")
        print(f"ROC-AUC:   {val_roc_auc:.4f}")
        
        print("\nClassification Report (Validation):")
        print(classification_report(self.y_val, y_val_pred, 
                                   target_names=['No Diabetes', 'Has Diabetes']))
        
        print("\nConfusion Matrix (Validation):")
        print(confusion_matrix(self.y_val, y_val_pred))
        
        # Test set evaluation
        y_test_pred = self.model.predict(self.X_test)
        y_test_proba = self.model.predict_proba(self.X_test)
        
        test_accuracy = accuracy_score(self.y_test, y_test_pred)
        test_precision = precision_score(self.y_test, y_test_pred, average='weighted')
        test_recall = recall_score(self.y_test, y_test_pred, average='weighted')
        test_f1 = f1_score(self.y_test, y_test_pred, average='weighted')
        
        try:
            test_roc_auc = roc_auc_score(self.y_test, y_test_proba[:, 1])
        except:
            test_roc_auc = 0.0
        
        print("\n=== Test Set Performance ===")
        print(f"Accuracy:  {test_accuracy:.4f}")
        print(f"Precision: {test_precision:.4f}")
        print(f"Recall:    {test_recall:.4f}")
        print(f"F1-Score:  {test_f1:.4f}")
        print(f"ROC-AUC:   {test_roc_auc:.4f}")
        
        print("\nClassification Report (Test):")
        print(classification_report(self.y_test, y_test_pred,
                                   target_names=['No Diabetes', 'Has Diabetes']))
        
        print("\nConfusion Matrix (Test):")
        print(confusion_matrix(self.y_test, y_test_pred))
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n=== Feature Importance ===")
        print(feature_importance.to_string(index=False))
        
        # Store metrics
        self.metrics = {
            'val_accuracy': val_accuracy,
            'val_precision': val_precision,
            'val_recall': val_recall,
            'val_f1': val_f1,
            'val_roc_auc': val_roc_auc,
            'test_accuracy': test_accuracy,
            'test_precision': test_precision,
            'test_recall': test_recall,
            'test_f1': test_f1,
            'test_roc_auc': test_roc_auc,
            'feature_importance': feature_importance.to_dict('records')
        }
        
    def save_model(self, output_dir: str = "backend/app/ml/models"):
        """
        Save the trained model with metadata.
        
        Args:
            output_dir: Directory to save the model
        """
        print(f"\nSaving model to {output_dir}...")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create label encoder for compatibility
        from sklearn.preprocessing import LabelEncoder
        label_encoder = LabelEncoder()
        label_encoder.fit(['No Diabetes', 'Has Diabetes'])
        
        # Create model bundle
        model_bundle = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': label_encoder,
            'feature_list': self.feature_names,
            'version': self.version,
            'training_date': datetime.now().isoformat(),
            'metrics': self.metrics
        }
        
        # Save model
        model_filename = f"{self.model_name}_{self.version}.pkl"
        model_path = output_path / model_filename
        joblib.dump(model_bundle, model_path)
        
        print(f"✓ Model saved to: {model_path}")
        
        return str(model_path)
    
    def register_model_in_db(self, model_path: str):
        """
        Register the trained model in the database.
        
        Args:
            model_path: Path to the saved model file
        """
        print("\nRegistering model in database...")
        
        db = SessionLocal()
        try:
            # Deactivate all existing models
            db.query(MLModelMetadata).update({'is_active': False})
            
            # Create new model metadata
            model_metadata = MLModelMetadata(
                model_name=self.model_name,
                model_type=self.model_type,
                version=self.version,
                model_path=model_path,
                accuracy=self.metrics['test_accuracy'],
                precision_type1=self.metrics['test_precision'],
                precision_type2=self.metrics['test_precision'],
                recall=self.metrics['test_recall'],
                f1_score=self.metrics['test_f1'],
                training_date=datetime.now(),
                is_active=True,
                hyperparameters={
                    'n_estimators': 200,
                    'max_depth': 10,
                    'min_samples_split': 10,
                    'min_samples_leaf': 4,
                    'max_features': 'sqrt',
                    'class_weight': 'balanced'
                },
                feature_importance=self.metrics['feature_importance']
            )
            
            db.add(model_metadata)
            db.commit()
            db.refresh(model_metadata)
            
            print(f"✓ Model registered with ID: {model_metadata.model_id}")
            print(f"✓ Model version: {self.version}")
            print(f"✓ Model is now active")
            
        except Exception as e:
            db.rollback()
            print(f"✗ Failed to register model in database: {e}")
            raise
        finally:
            db.close()
    
    def run(self):
        """Run the complete training pipeline."""
        print("=" * 60)
        print("Diabetes Prediction Model Training")
        print("=" * 60)
        
        try:
            # Load datasets
            self.load_datasets()
            
            # Train model
            self.train_model()
            
            # Evaluate model
            self.evaluate_model()
            
            # Save model
            model_path = self.save_model()
            
            # Register in database
            self.register_model_in_db(model_path)
            
            print("\n" + "=" * 60)
            print("✓ Training pipeline completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Training pipeline failed: {e}")
            raise


def main():
    """Main entry point for training script."""
    trainer = DiabetesModelTrainer()
    trainer.run()


if __name__ == "__main__":
    main()
