"""
Check the structure of the trained model file.

Usage:
    python scripts/check_model.py
"""

import joblib
from pathlib import Path

model_path = Path(__file__).parent.parent / "ml_models" / "diabetes_model.pkl"

print("=" * 60)
print("Checking Model File Structure")
print("=" * 60)
print(f"Model path: {model_path}")
print(f"File exists: {model_path.exists()}")

if not model_path.exists():
    print("\n❌ Model file not found!")
    print("Run: python scripts/train_models.py")
    exit(1)

print("\nLoading model...")
try:
    model_data = joblib.load(model_path)
    
    print("\n✓ Model loaded successfully!")
    print(f"\nModel type: {type(model_data)}")
    
    if isinstance(model_data, dict):
        print("\n📦 Model Bundle Contents:")
        for key in model_data.keys():
            print(f"  - {key}: {type(model_data[key])}")
        
        if 'feature_list' in model_data:
            print(f"\n📋 Features ({len(model_data['feature_list'])}):")
            for i, feature in enumerate(model_data['feature_list'], 1):
                print(f"  {i}. {feature}")
        else:
            print("\n⚠️  Warning: 'feature_list' not found in model bundle")
            print("   The model might be in old format")
    else:
        print("\n⚠️  Model is not a dictionary bundle")
        print("   Expected format: {'model': ..., 'scaler': ..., 'label_encoder': ..., 'feature_list': ...}")
        print("   Please retrain the model using scripts/train_models.py")
        
except Exception as e:
    print(f"\n❌ Error loading model: {e}")
    import traceback
    traceback.print_exc()
