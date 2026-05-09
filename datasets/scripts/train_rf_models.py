"""
Train Random Forest Models for DiaTracker
==========================================

Purpose: Train two Random Forest models:
- RF #1: Glucose Predictor (predicts 1-hour post-meal glucose)
- RF #2: Risk Classifier (classifies Low/Mid/High risk)

Author: DiaTracker Enhancement Project
Date: May 6, 2026
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import warnings
warnings.filterwarnings('ignore')

# File paths
DATA_DIR = Path(__file__).parent
NHANES_FILE = DATA_DIR / "nhanes_2021_2023_processed.csv"
OUTPUT_DIR = DATA_DIR.parent.parent / "backend" / "ml_models"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    """Load NHANES processed data."""
    print("=" * 80)
    print("STEP 1: Loading Data")
    print("=" * 80)
    
    df = pd.read_csv(NHANES_FILE)
    print(f"\nLoaded {len(df)} participants")
    print(f"Columns: {list(df.columns)}")
    
    return df


def prepare_rf1_data(df):
    """
    Prepare data for RF #1 (Glucose Predictor).
    
    Note: Since we don't have actual 1-hour post-meal glucose in NHANES,
    we'll simulate it based on fasting glucose + meal composition.
    
    Simulation formula (based on clinical research):
    glucose_1hr ≈ fasting_glucose + (GL × 0.5) + random_variation
    
    This is a placeholder until we get real post-meal glucose data.
    """
    print("\n" + "=" * 80)
    print("STEP 2: Preparing RF #1 Data (Glucose Predictor)")
    print("=" * 80)
    
    print("\n⚠️ NOTE: Simulating glucose_1hr since NHANES doesn't have post-meal glucose")
    print("   Formula: glucose_1hr ≈ fasting_glucose + (available_carbs × 0.25)")
    
    # Features for RF #1 (8 features)
    feature_cols = [
        'fasting_glucose',
        'available_carbs_g',
        'fat_g',
        'protein_g',
        'fiber_g',
        'BMI',
        'age',
        'gender'
    ]
    
    # Filter participants with complete dietary data
    df_rf1 = df[feature_cols].copy()
    df_rf1 = df_rf1.dropna()
    
    print(f"\nParticipants with complete dietary data: {len(df_rf1)}")
    
    # Encode gender
    df_rf1['gender'] = df_rf1['gender'].map({'Male': 1, 'Female': 0})
    
    # Simulate glucose_1hr (placeholder)
    # In reality, this would come from CGM data or OGTT
    np.random.seed(42)
    df_rf1['glucose_1hr'] = (
        df_rf1['fasting_glucose'] + 
        (df_rf1['available_carbs_g'] * 0.25) +
        np.random.normal(0, 10, len(df_rf1))  # Add some noise
    )
    
    # Clip to realistic range (70-300 mg/dL)
    df_rf1['glucose_1hr'] = df_rf1['glucose_1hr'].clip(70, 300)
    
    print(f"\nSimulated glucose_1hr statistics:")
    print(f"  Mean: {df_rf1['glucose_1hr'].mean():.1f} mg/dL")
    print(f"  Median: {df_rf1['glucose_1hr'].median():.1f} mg/dL")
    print(f"  Min: {df_rf1['glucose_1hr'].min():.1f} mg/dL")
    print(f"  Max: {df_rf1['glucose_1hr'].max():.1f} mg/dL")
    
    X = df_rf1[feature_cols]
    y = df_rf1['glucose_1hr']
    
    print(f"\nFeatures shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    return X, y, feature_cols


def prepare_rf2_data(df):
    """Prepare data for RF #2 (Risk Classifier)."""
    print("\n" + "=" * 80)
    print("STEP 3: Preparing RF #2 Data (Risk Classifier)")
    print("=" * 80)
    
    # Features for RF #2 (5 features: added family_history)
    feature_cols = [
        'fasting_glucose',
        'BMI',
        'age',
        'gender',
        'family_history'
    ]
    
    target_col = 'risk_level'
    
    # Filter participants with complete data
    df_rf2 = df[feature_cols + [target_col]].copy()
    df_rf2 = df_rf2.dropna()
    
    print(f"\nParticipants with complete data: {len(df_rf2)}")
    
    # Encode gender
    df_rf2['gender'] = df_rf2['gender'].map({'Male': 1, 'Female': 0})
    
    # Encode family_history
    df_rf2['family_history'] = df_rf2['family_history'].map({'Yes': 1, 'No': 0})
    
    # Check class distribution
    print(f"\nClass distribution:")
    print(df_rf2[target_col].value_counts())
    print(f"\nClass percentages:")
    print(df_rf2[target_col].value_counts(normalize=True) * 100)
    
    X = df_rf2[feature_cols]
    y = df_rf2[target_col]
    
    # Encode target (Low=0, Mid=1, High=2)
    y_encoded = y.map({'Low': 0, 'Mid': 1, 'High': 2})
    
    print(f"\nFeatures shape: {X.shape}")
    print(f"Target shape: {y_encoded.shape}")
    
    return X, y_encoded, feature_cols


def train_rf1(X, y, feature_cols):
    """Train RF #1 (Glucose Predictor)."""
    print("\n" + "=" * 80)
    print("STEP 4: Training RF #1 (Glucose Predictor)")
    print("=" * 80)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train model
    print("\nTraining Random Forest Regressor...")
    print("  Parameters:")
    print("    - n_estimators: 100")
    print("    - max_depth: None")
    print("    - min_samples_split: 2")
    print("    - random_state: 42")
    
    rf1 = RandomForestRegressor(
        n_estimators=100,
        max_depth=None,
        min_samples_split=2,
        random_state=42,
        n_jobs=-1
    )
    
    rf1.fit(X_train, y_train)
    print("\n✓ Training complete")
    
    # Evaluate
    y_pred = rf1.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n📊 Performance Metrics:")
    print(f"  RMSE: {rmse:.2f} mg/dL")
    print(f"  MAE: {mae:.2f} mg/dL")
    print(f"  R²: {r2:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf1.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n📋 Feature Importance:")
    for idx, row in feature_importance.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    # Cross-validation
    print(f"\n🔄 Cross-Validation (5-fold):")
    cv_scores = cross_val_score(rf1, X, y, cv=5, scoring='r2')
    print(f"  R² scores: {cv_scores}")
    print(f"  Mean R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    return rf1, X_test, y_test, y_pred


def train_rf2(X, y, feature_cols):
    """Train RF #2 (Risk Classifier)."""
    print("\n" + "=" * 80)
    print("STEP 5: Training RF #2 (Risk Classifier)")
    print("=" * 80)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train model
    print("\nTraining Random Forest Classifier...")
    print("  Parameters:")
    print("    - n_estimators: 100")
    print("    - max_depth: None")
    print("    - min_samples_split: 2")
    print("    - random_state: 42")
    
    rf2 = RandomForestClassifier(
        n_estimators=100,
        max_depth=None,
        min_samples_split=2,
        random_state=42,
        n_jobs=-1
    )
    
    rf2.fit(X_train, y_train)
    print("\n✓ Training complete")
    
    # Evaluate
    y_pred = rf2.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    print(f"\n📊 Performance Metrics:")
    print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"  Recall: {recall:.4f} ({recall*100:.2f}%)")
    print(f"  F1-Score: {f1:.4f} ({f1*100:.2f}%)")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n📈 Confusion Matrix:")
    print("     Predicted:")
    print("       Low  Mid  High")
    print(f"Low   {cm[0][0]:4d} {cm[0][1]:4d} {cm[0][2]:4d}")
    print(f"Mid   {cm[1][0]:4d} {cm[1][1]:4d} {cm[1][2]:4d}")
    print(f"High  {cm[2][0]:4d} {cm[2][1]:4d} {cm[2][2]:4d}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf2.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n📋 Feature Importance:")
    for idx, row in feature_importance.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    # Cross-validation
    print(f"\n🔄 Cross-Validation (5-fold):")
    cv_scores = cross_val_score(rf2, X, y, cv=5, scoring='accuracy')
    print(f"  Accuracy scores: {cv_scores}")
    print(f"  Mean Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    return rf2, X_test, y_test, y_pred


def save_models(rf1, rf2, rf1_features, rf2_features):
    """Save trained models."""
    print("\n" + "=" * 80)
    print("STEP 6: Saving Models")
    print("=" * 80)
    
    # Save RF #1
    rf1_path = OUTPUT_DIR / "glucose_predictor_rf.pkl"
    with open(rf1_path, 'wb') as f:
        pickle.dump(rf1, f)
    print(f"\n✓ Saved RF #1 to: {rf1_path}")
    
    # Save RF #2
    rf2_path = OUTPUT_DIR / "risk_classifier_rf.pkl"
    with open(rf2_path, 'wb') as f:
        pickle.dump(rf2, f)
    print(f"✓ Saved RF #2 to: {rf2_path}")
    
    # Save feature names
    rf1_features_path = OUTPUT_DIR / "glucose_predictor_features.txt"
    with open(rf1_features_path, 'w') as f:
        f.write('\n'.join(rf1_features))
    print(f"✓ Saved RF #1 features to: {rf1_features_path}")
    
    rf2_features_path = OUTPUT_DIR / "risk_classifier_features.txt"
    with open(rf2_features_path, 'w') as f:
        f.write('\n'.join(rf2_features))
    print(f"✓ Saved RF #2 features to: {rf2_features_path}")
    
    # Save model metadata
    metadata_path = OUTPUT_DIR / "model_metadata.txt"
    with open(metadata_path, 'w') as f:
        f.write("DiaTracker Random Forest Models\n")
        f.write("=" * 80 + "\n\n")
        f.write("Date: May 6, 2026\n")
        f.write("Algorithm: Random Forest\n\n")
        
        f.write("RF #1 (Glucose Predictor):\n")
        f.write("  Type: Random Forest Regressor\n")
        f.write("  Features: 8\n")
        f.write(f"  Feature list: {', '.join(rf1_features)}\n")
        f.write("  Output: glucose_1hr (mg/dL)\n\n")
        
        f.write("RF #2 (Risk Classifier):\n")
        f.write("  Type: Random Forest Classifier\n")
        f.write("  Features: 5\n")
        f.write(f"  Feature list: {', '.join(rf2_features)}\n")
        f.write("  Output: Low/Mid/High risk\n\n")
        
        f.write("Citations:\n")
        f.write("  - Breiman L. 2001. Random Forests. Machine Learning 45(1):5-32.\n")
        f.write("  - ADA. 2024. Standards of Care in Diabetes—2024. Diabetes Care 47(Suppl 1):S20-S42.\n")
        f.write("  - CDC. 2023. NHANES 2021-2023.\n")
    
    print(f"✓ Saved metadata to: {metadata_path}")


def main():
    """Main training pipeline."""
    print("\n" + "=" * 80)
    print("TRAIN RANDOM FOREST MODELS FOR DIATRACKER")
    print("=" * 80)
    print("\nThis script will:")
    print("  1. Load NHANES data")
    print("  2. Prepare data for RF #1 (Glucose Predictor)")
    print("  3. Prepare data for RF #2 (Risk Classifier)")
    print("  4. Train RF #1")
    print("  5. Train RF #2")
    print("  6. Save models")
    print("\n" + "=" * 80)
    
    try:
        # Load data
        df = load_data()
        
        # Prepare RF #1 data
        X_rf1, y_rf1, rf1_features = prepare_rf1_data(df)
        
        # Prepare RF #2 data
        X_rf2, y_rf2, rf2_features = prepare_rf2_data(df)
        
        # Train RF #1
        rf1, X_test_rf1, y_test_rf1, y_pred_rf1 = train_rf1(X_rf1, y_rf1, rf1_features)
        
        # Train RF #2
        rf2, X_test_rf2, y_test_rf2, y_pred_rf2 = train_rf2(X_rf2, y_rf2, rf2_features)
        
        # Save models
        save_models(rf1, rf2, rf1_features, rf2_features)
        
        print("\n" + "=" * 80)
        print("✓ TRAINING COMPLETE!")
        print("=" * 80)
        print("\nModels saved to:", OUTPUT_DIR)
        print("\nNext steps:")
        print("  1. Test models with sample data")
        print("  2. Integrate into backend API")
        print("  3. Update frontend to use new models")
        print("  4. Deploy to production")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
