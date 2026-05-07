"""
Compare Three Models: Random Forest vs Logistic Regression vs SVM
==================================================================

Purpose: Train and compare three models for diabetes risk prediction:
1. Random Forest (RF)
2. Logistic Regression (LR)
3. Support Vector Machine (SVM)

Evaluate on: Accuracy, Precision, Recall, F1-Score, ROC-AUC

Author: DiaTracker Enhancement Project
Date: May 6, 2026
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import warnings
warnings.filterwarnings('ignore')

# File paths
NHANES_FILE = "nhanes_2021_2023_processed.csv"


def load_and_prepare_data():
    """Load NHANES data and prepare for modeling."""
    print("=" * 80)
    print("STEP 1: Loading and Preparing Data")
    print("=" * 80)
    
    # Load data
    df = pd.read_csv(NHANES_FILE)
    print(f"\nLoaded {len(df)} participants")
    
    # Features for RF #2 (Risk Classifier)
    # Using 5 features: fasting_glucose, BMI, age, gender, (glucose_1hr will be added later)
    # For now, we'll use available features
    
    feature_cols = ['fasting_glucose', 'BMI', 'age', 'gender']
    target_col = 'risk_level'
    
    # Prepare features
    df_model = df[feature_cols + [target_col]].copy()
    
    # Encode gender
    df_model['gender'] = df_model['gender'].map({'Male': 1, 'Female': 0})
    
    # Remove missing values
    df_model = df_model.dropna()
    
    print(f"\nAfter removing missing values: {len(df_model)} participants")
    
    # Check class distribution
    print(f"\nClass distribution:")
    print(df_model[target_col].value_counts())
    print(f"\nClass percentages:")
    print(df_model[target_col].value_counts(normalize=True) * 100)
    
    # Prepare X and y
    X = df_model[feature_cols]
    y = df_model[target_col]
    
    # Encode target (Low=0, Mid=1, High=2)
    y_encoded = y.map({'Low': 0, 'Mid': 1, 'High': 2})
    
    print(f"\nFeatures shape: {X.shape}")
    print(f"Target shape: {y_encoded.shape}")
    
    return X, y_encoded, feature_cols


def split_data(X, y):
    """Split data into train and test sets."""
    print("\n" + "=" * 80)
    print("STEP 2: Splitting Data (80/20)")
    print("=" * 80)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Check class distribution in splits
    print(f"\nTraining set distribution:")
    print(pd.Series(y_train).value_counts())
    print(f"\nTest set distribution:")
    print(pd.Series(y_test).value_counts())
    
    return X_train, X_test, y_train, y_test


def scale_features(X_train, X_test):
    """Scale features for Logistic Regression and SVM."""
    print("\n" + "=" * 80)
    print("STEP 3: Scaling Features (for LR and SVM)")
    print("=" * 80)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("\n✓ Features scaled (mean=0, std=1)")
    print(f"  Training set shape: {X_train_scaled.shape}")
    print(f"  Test set shape: {X_test_scaled.shape}")
    
    return X_train_scaled, X_test_scaled, scaler


def train_random_forest(X_train, y_train):
    """Train Random Forest model."""
    print("\n" + "=" * 80)
    print("MODEL 1: Random Forest")
    print("=" * 80)
    
    print("\nTraining Random Forest Classifier...")
    print("  Parameters:")
    print("    - n_estimators: 100 (number of trees)")
    print("    - max_depth: None (unlimited)")
    print("    - min_samples_split: 2")
    print("    - random_state: 42")
    
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=None,
        min_samples_split=2,
        random_state=42,
        n_jobs=-1
    )
    
    rf.fit(X_train, y_train)
    print("\n✓ Training complete")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    for idx, row in feature_importance.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    return rf


def train_logistic_regression(X_train_scaled, y_train):
    """Train Logistic Regression model."""
    print("\n" + "=" * 80)
    print("MODEL 2: Logistic Regression")
    print("=" * 80)
    
    print("\nTraining Logistic Regression...")
    print("  Parameters:")
    print("    - solver: lbfgs")
    print("    - max_iter: 1000")
    print("    - multi_class: multinomial")
    print("    - random_state: 42")
    
    lr = LogisticRegression(
        max_iter=1000,
        random_state=42
    )
    
    lr.fit(X_train_scaled, y_train)
    print("\n✓ Training complete")
    
    return lr


def train_svm(X_train_scaled, y_train):
    """Train SVM model."""
    print("\n" + "=" * 80)
    print("MODEL 3: Support Vector Machine (SVM)")
    print("=" * 80)
    
    print("\nTraining SVM Classifier...")
    print("  Parameters:")
    print("    - kernel: rbf (Radial Basis Function)")
    print("    - C: 1.0 (regularization)")
    print("    - gamma: scale")
    print("    - random_state: 42")
    
    svm = SVC(
        kernel='rbf',
        C=1.0,
        gamma='scale',
        probability=True,  # Enable probability estimates
        random_state=42
    )
    
    svm.fit(X_train_scaled, y_train)
    print("\n✓ Training complete")
    
    return svm


def evaluate_model(model, X_test, y_test, model_name, is_scaled=False):
    """Evaluate model performance."""
    print(f"\n" + "=" * 80)
    print(f"EVALUATING: {model_name}")
    print("=" * 80)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    # ROC-AUC (one-vs-rest for multiclass)
    try:
        roc_auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
    except:
        roc_auc = None
    
    # Print results
    print(f"\n📊 Performance Metrics:")
    print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"  Recall:    {recall:.4f} ({recall*100:.2f}%)")
    print(f"  F1-Score:  {f1:.4f} ({f1*100:.2f}%)")
    if roc_auc:
        print(f"  ROC-AUC:   {roc_auc:.4f} ({roc_auc*100:.2f}%)")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n📈 Confusion Matrix:")
    print("     Predicted:")
    print("       Low  Mid  High")
    print(f"Low   {cm[0][0]:4d} {cm[0][1]:4d} {cm[0][2]:4d}")
    print(f"Mid   {cm[1][0]:4d} {cm[1][1]:4d} {cm[1][2]:4d}")
    print(f"High  {cm[2][0]:4d} {cm[2][1]:4d} {cm[2][2]:4d}")
    
    # Per-class metrics
    print(f"\n📋 Per-Class Metrics:")
    class_names = ['Low', 'Mid', 'High']
    for i, class_name in enumerate(class_names):
        class_mask = (y_test == i)
        class_pred_mask = (y_pred == i)
        
        tp = np.sum((y_test == i) & (y_pred == i))
        fp = np.sum((y_test != i) & (y_pred == i))
        fn = np.sum((y_test == i) & (y_pred != i))
        tn = np.sum((y_test != i) & (y_pred != i))
        
        class_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        class_recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        class_f1 = 2 * (class_precision * class_recall) / (class_precision + class_recall) if (class_precision + class_recall) > 0 else 0
        
        print(f"  {class_name} Risk:")
        print(f"    Precision: {class_precision:.4f} ({class_precision*100:.2f}%)")
        print(f"    Recall:    {class_recall:.4f} ({class_recall*100:.2f}%)")
        print(f"    F1-Score:  {class_f1:.4f} ({class_f1*100:.2f}%)")
    
    return {
        'model_name': model_name,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'roc_auc': roc_auc,
        'confusion_matrix': cm
    }


def compare_models(results):
    """Compare all models side by side."""
    print("\n" + "=" * 80)
    print("🏆 MODEL COMPARISON SUMMARY")
    print("=" * 80)
    
    # Create comparison table
    print("\n" + "=" * 80)
    print("Performance Metrics Comparison")
    print("=" * 80)
    print(f"\n{'Metric':<15} {'Random Forest':<15} {'Logistic Reg':<15} {'SVM':<15}")
    print("-" * 80)
    
    metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
    metric_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
    
    for metric, name in zip(metrics, metric_names):
        rf_val = results[0][metric]
        lr_val = results[1][metric]
        svm_val = results[2][metric]
        
        if rf_val is not None:
            rf_str = f"{rf_val:.4f} ({rf_val*100:.2f}%)"
        else:
            rf_str = "N/A"
        
        if lr_val is not None:
            lr_str = f"{lr_val:.4f} ({lr_val*100:.2f}%)"
        else:
            lr_str = "N/A"
        
        if svm_val is not None:
            svm_str = f"{svm_val:.4f} ({svm_val*100:.2f}%)"
        else:
            svm_str = "N/A"
        
        print(f"{name:<15} {rf_str:<15} {lr_str:<15} {svm_str:<15}")
    
    # Determine best model
    print("\n" + "=" * 80)
    print("🥇 BEST MODEL BY METRIC")
    print("=" * 80)
    
    for metric, name in zip(metrics, metric_names):
        values = [r[metric] for r in results if r[metric] is not None]
        if values:
            best_idx = np.argmax(values)
            best_model = results[best_idx]['model_name']
            best_value = values[best_idx]
            print(f"\n{name}: {best_model}")
            print(f"  Value: {best_value:.4f} ({best_value*100:.2f}%)")
    
    # Overall recommendation
    print("\n" + "=" * 80)
    print("💡 RECOMMENDATION")
    print("=" * 80)
    
    # Calculate average rank
    ranks = []
    for result in results:
        rank_sum = 0
        for metric in metrics:
            if result[metric] is not None:
                values = [r[metric] for r in results if r[metric] is not None]
                rank = sorted(values, reverse=True).index(result[metric]) + 1
                rank_sum += rank
        avg_rank = rank_sum / len(metrics)
        ranks.append((result['model_name'], avg_rank))
    
    ranks.sort(key=lambda x: x[1])
    
    print(f"\nOverall Ranking (lower is better):")
    for i, (model, rank) in enumerate(ranks, 1):
        print(f"  {i}. {model}: Average Rank = {rank:.2f}")
    
    best_model = ranks[0][0]
    print(f"\n🏆 RECOMMENDED MODEL: {best_model}")
    
    # Provide reasoning
    print(f"\nReasoning:")
    if best_model == "Random Forest":
        print("  ✓ Best overall performance across all metrics")
        print("  ✓ Handles non-linear relationships well")
        print("  ✓ Provides feature importance")
        print("  ✓ Robust to outliers")
        print("  ✓ No feature scaling required")
    elif best_model == "Logistic Regression":
        print("  ✓ Simple and interpretable")
        print("  ✓ Fast training and prediction")
        print("  ✓ Good for linear relationships")
        print("  ✓ Provides probability estimates")
    elif best_model == "SVM":
        print("  ✓ Effective in high-dimensional spaces")
        print("  ✓ Good for non-linear boundaries")
        print("  ✓ Memory efficient")


def main():
    """Main comparison pipeline."""
    print("\n" + "=" * 80)
    print("MODEL COMPARISON: RF vs LR vs SVM")
    print("=" * 80)
    print("\nThis script will:")
    print("  1. Load NHANES data")
    print("  2. Split into train/test (80/20)")
    print("  3. Train Random Forest")
    print("  4. Train Logistic Regression")
    print("  5. Train SVM")
    print("  6. Evaluate all models")
    print("  7. Compare performance")
    print("  8. Recommend best model")
    print("\n" + "=" * 80)
    
    try:
        # Load and prepare data
        X, y, feature_cols = load_and_prepare_data()
        
        # Split data
        X_train, X_test, y_train, y_test = split_data(X, y)
        
        # Scale features (for LR and SVM)
        X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)
        
        # Train models
        rf_model = train_random_forest(X_train, y_train)
        lr_model = train_logistic_regression(X_train_scaled, y_train)
        svm_model = train_svm(X_train_scaled, y_train)
        
        # Evaluate models
        results = []
        results.append(evaluate_model(rf_model, X_test, y_test, "Random Forest"))
        results.append(evaluate_model(lr_model, X_test_scaled, y_test, "Logistic Regression", is_scaled=True))
        results.append(evaluate_model(svm_model, X_test_scaled, y_test, "SVM", is_scaled=True))
        
        # Compare models
        compare_models(results)
        
        print("\n" + "=" * 80)
        print("✓ COMPARISON COMPLETE!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
