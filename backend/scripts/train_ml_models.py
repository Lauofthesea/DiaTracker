"""
Script to train ML models for diabetes prediction.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.services.ml_training_service import MLTrainingService


def generate_sample_data(n_samples: int = 1000) -> tuple:
    """
    Generate sample diabetes data for training.
    
    Args:
        n_samples: Number of samples to generate
    
    Returns:
        Tuple of (features_df, labels_series)
    """
    np.random.seed(42)
    
    # Generate features
    data = {
        'weight_kg': np.random.uniform(50, 120, n_samples),
        'blood_sugar_mgdl': np.random.uniform(70, 300, n_samples),
        'age': np.random.randint(20, 80, n_samples),
        'bmi': np.random.uniform(18, 40, n_samples),
        'frequent_urination': np.random.randint(0, 2, n_samples),
        'excessive_thirst': np.random.randint(0, 2, n_samples),
        'fatigue': np.random.randint(0, 2, n_samples),
        'blurred_vision': np.random.randint(0, 2, n_samples),
        'slow_healing': np.random.randint(0, 2, n_samples),
    }
    
    X = pd.DataFrame(data)
    
    # Generate labels based on features (simplified logic)
    labels = []
    for i in range(n_samples):
        blood_sugar = data['blood_sugar_mgdl'][i]
        age = data['age'][i]
        bmi = data['bmi'][i]
        symptoms = sum([
            data['frequent_urination'][i],
            data['excessive_thirst'][i],
            data['fatigue'][i],
            data['blurred_vision'][i],
            data['slow_healing'][i]
        ])
        
        # Simple classification logic
        if blood_sugar > 200 and age < 30 and symptoms >= 3:
            labels.append('Type 1')
        elif blood_sugar > 180 and bmi > 30 and symptoms >= 2:
            labels.append('Type 2')
        else:
            labels.append('No Diabetes')
    
    y = pd.Series(labels, name='diagnosis')
    
    return X, y


def main():
    """Main training function."""
    print("Generating sample training data...")
    X, y = generate_sample_data(n_samples=1000)
    
    print(f"\nDataset shape: {X.shape}")
    print(f"Class distribution:\n{y.value_counts()}")
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        # Initialize training service
        training_service = MLTrainingService(db)
        
        # Train all models
        model_results = training_service.train_all_models(X, y)
        
        print("\n" + "="*50)
        print("Training Summary:")
        print("="*50)
        for model_name, (model, metrics) in model_results.items():
            print(f"\n{model_name}:")
            print(f"  Accuracy: {metrics['accuracy']:.4f}")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall: {metrics['recall']:.4f}")
            print(f"  F1-Score: {metrics['f1_score']:.4f}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
