"""
Register trained ML model in the database.

This script creates the necessary database record for the trained diabetes model
so the prediction service can load it.

Usage:
    python scripts/register_model.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import SessionLocal
from app.models.ml_model_metadata import MLModelMetadata


def register_diabetes_model():
    """Register the diabetes prediction model in the database."""
    db = SessionLocal()
    
    try:
        # Check if model already exists
        existing_model = db.query(MLModelMetadata).filter(
            MLModelMetadata.model_name == "Diabetes Risk Classifier"
        ).first()
        
        if existing_model:
            print(f"Model already registered: {existing_model.model_name} v{existing_model.version}")
            print(f"Setting as active model...")
            
            # Deactivate all other models
            db.query(MLModelMetadata).update({"is_active": False})
            
            # Activate this model
            existing_model.is_active = True
            db.commit()
            
            print(f"✓ Model activated successfully")
            return
        
        # Deactivate any existing active models
        db.query(MLModelMetadata).update({"is_active": False})
        
        # Create new model metadata record
        model_path = str(Path(__file__).parent.parent / "ml_models" / "diabetes_model.pkl")
        
        model_metadata = MLModelMetadata(
            model_name="Diabetes Risk Classifier",
            model_type="RandomForestClassifier",
            version="1.0.0",
            model_path=model_path,
            accuracy=0.81,  # From training results
            precision_type1=0.80,
            precision_type2=0.82,
            recall=0.81,
            f1_score=0.81,
            roc_auc=0.85,
            training_date=datetime.utcnow(),
            is_active=True,
            description="Diabetes risk prediction model trained on health metrics including weight, blood sugar, age, BMI, and symptoms."
        )
        
        db.add(model_metadata)
        db.commit()
        db.refresh(model_metadata)
        
        print("=" * 60)
        print("Model Registered Successfully!")
        print("=" * 60)
        print(f"Model Name: {model_metadata.model_name}")
        print(f"Version: {model_metadata.version}")
        print(f"Type: {model_metadata.model_type}")
        print(f"Path: {model_metadata.model_path}")
        print(f"Accuracy: {model_metadata.accuracy:.2%}")
        print(f"ROC-AUC: {model_metadata.roc_auc:.4f}")
        print(f"Active: {model_metadata.is_active}")
        print(f"Training Date: {model_metadata.training_date}")
        print("\n✓ Model is now ready for predictions!")
        
    except Exception as e:
        print(f"❌ Error registering model: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("ML Model Registration Script")
    print("=" * 60)
    register_diabetes_model()
