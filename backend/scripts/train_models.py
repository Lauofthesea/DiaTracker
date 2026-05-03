"""
Script to train ML models using the provided datasets.

This script trains two models:
1. Diabetes Prediction Model - Predicts diabetes risk from health metrics
2. Food Classification Model - Classifies foods by diabetes risk level

Usage:
    python scripts/train_models.py
"""

import pandas as pd
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib
import sys

# Paths
DATASETS_DIR = Path(__file__).parent.parent.parent / "Datasets"
MODELS_DIR = Path(__file__).parent.parent / "ml_models"
MODELS_DIR.mkdir(exist_ok=True)


def train_diabetes_model():
    """Train diabetes prediction model."""
    print("=" * 60)
    print("Training Diabetes Prediction Model")
    print("=" * 60)
    
    # Load data
    print("\nLoading datasets...")
    X_train = pd.read_csv(DATASETS_DIR / "diabetes_X_train.csv")
    y_train = pd.read_csv(DATASETS_DIR / "diabetes_y_train.csv")["Outcome"]
    X_val = pd.read_csv(DATASETS_DIR / "diabetes_X_val.csv")
    y_val = pd.read_csv(DATASETS_DIR / "diabetes_y_val.csv")["Outcome"]
    X_test = pd.read_csv(DATASETS_DIR / "diabetes_X_test.csv")
    y_test = pd.read_csv(DATASETS_DIR / "diabetes_y_test.csv")["Outcome"]
    
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Features: {list(X_train.columns)}")
    
    # Load scaler
    with open(DATASETS_DIR / "diabetes_scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight="balanced"
    )
    
    print("\nTraining model...")
    model.fit(X_train, y_train)
    
    # Evaluate on validation set
    y_val_pred = model.predict(X_val)
    y_val_proba = model.predict_proba(X_val)
    
    print("\n" + "=" * 60)
    print("Validation Set Performance")
    print("=" * 60)
    print(f"ROC-AUC Score: {roc_auc_score(y_val, y_val_proba[:, 1]):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_val, y_val_pred, target_names=["No Diabetes", "Has Diabetes"]))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_val, y_val_pred))
    
    # Evaluate on test set
    y_test_pred = model.predict(X_test)
    y_test_proba = model.predict_proba(X_test)
    
    print("\n" + "=" * 60)
    print("Test Set Performance")
    print("=" * 60)
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_test_proba[:, 1]):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_test_pred, target_names=["No Diabetes", "Has Diabetes"]))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n" + "=" * 60)
    print("Feature Importance")
    print("=" * 60)
    print(feature_importance.to_string(index=False))
    
    # Save model
    model_path = MODELS_DIR / "diabetes_model.pkl"
    scaler_path = MODELS_DIR / "diabetes_scaler.pkl"
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"\n✓ Model saved to: {model_path}")
    print(f"✓ Scaler saved to: {scaler_path}")
    
    return model, scaler


def train_food_classification_model():
    """Train food classification model."""
    print("\n" + "=" * 60)
    print("Training Food Classification Model")
    print("=" * 60)
    
    # Load data
    print("\nLoading datasets...")
    X_train = pd.read_csv(DATASETS_DIR / "food_X_train.csv")
    y_train = pd.read_csv(DATASETS_DIR / "food_y_train.csv")["target"]
    X_val = pd.read_csv(DATASETS_DIR / "food_X_val.csv")
    y_val = pd.read_csv(DATASETS_DIR / "food_y_val.csv")["target"]
    X_test = pd.read_csv(DATASETS_DIR / "food_X_test.csv")
    y_test = pd.read_csv(DATASETS_DIR / "food_y_test.csv")["target"]
    
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Features: {list(X_train.columns)}")
    
    # Load encoders and scaler
    with open(DATASETS_DIR / "food_encoders.pkl", "rb") as f:
        encoders = pickle.load(f)
    
    with open(DATASETS_DIR / "food_scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    
    # Class distribution
    print("\nClass Distribution:")
    print(y_train.value_counts())
    
    # Train model with class weights due to imbalance
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42,
        class_weight="balanced"  # Important for imbalanced data
    )
    
    print("\nTraining model...")
    model.fit(X_train, y_train)
    
    # Evaluate on validation set
    y_val_pred = model.predict(X_val)
    
    print("\n" + "=" * 60)
    print("Validation Set Performance")
    print("=" * 60)
    print("\nClassification Report:")
    print(classification_report(y_val, y_val_pred, target_names=encoders["target"].classes_))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_val, y_val_pred))
    
    # Evaluate on test set
    y_test_pred = model.predict(X_test)
    
    print("\n" + "=" * 60)
    print("Test Set Performance")
    print("=" * 60)
    print("\nClassification Report:")
    print(classification_report(y_test, y_test_pred, target_names=encoders["target"].classes_))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n" + "=" * 60)
    print("Feature Importance")
    print("=" * 60)
    print(feature_importance.to_string(index=False))
    
    # Save model
    model_path = MODELS_DIR / "food_classification_model.pkl"
    scaler_path = MODELS_DIR / "food_scaler.pkl"
    encoders_path = MODELS_DIR / "food_encoders.pkl"
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(encoders, encoders_path)
    
    print(f"\n✓ Model saved to: {model_path}")
    print(f"✓ Scaler saved to: {scaler_path}")
    print(f"✓ Encoders saved to: {encoders_path}")
    
    return model, scaler, encoders


def main():
    """Main training function."""
    print("ML Model Training Script")
    print("=" * 60)
    print(f"Datasets directory: {DATASETS_DIR}")
    print(f"Models output directory: {MODELS_DIR}")
    
    # Check if datasets exist
    if not DATASETS_DIR.exists():
        print(f"\n❌ Error: Datasets directory not found at {DATASETS_DIR}")
        print("Please ensure the Datasets folder is in the project root.")
        sys.exit(1)
    
    required_files = [
        "diabetes_X_train.csv",
        "diabetes_y_train.csv",
        "diabetes_scaler.pkl",
        "food_X_train.csv",
        "food_y_train.csv",
        "food_scaler.pkl",
        "food_encoders.pkl"
    ]
    
    missing_files = [f for f in required_files if not (DATASETS_DIR / f).exists()]
    if missing_files:
        print(f"\n❌ Error: Missing required dataset files:")
        for f in missing_files:
            print(f"  - {f}")
        sys.exit(1)
    
    print("\n✓ All required dataset files found")
    
    try:
        # Train diabetes model
        diabetes_model, diabetes_scaler = train_diabetes_model()
        
        # Train food classification model
        food_model, food_scaler, food_encoders = train_food_classification_model()
        
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review the model performance metrics above")
        print("2. Update the ML service to use the new models")
        print("3. Test the models with sample predictions")
        print("4. Deploy to production when ready")
        print("\nSee docs/DATASET_INTEGRATION_GUIDE.md for integration instructions")
        
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
