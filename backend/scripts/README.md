# Backend Scripts

This directory contains utility scripts for the ML Diabetes Tracker backend.

## Available Scripts

### train_models.py

Trains ML models using the preprocessed datasets from the `Datasets/` folder.

**Purpose:**
- Train diabetes prediction model (Random Forest)
- Train food classification model (Random Forest)
- Evaluate model performance
- Save trained models for production use

**Requirements:**
```bash
pip install pandas scikit-learn joblib
```

**Usage:**
```bash
cd backend
python scripts/train_models.py
```

**Output:**
- `ml_models/diabetes_model.pkl` - Trained diabetes prediction model
- `ml_models/diabetes_scaler.pkl` - Feature scaler for diabetes model
- `ml_models/food_classification_model.pkl` - Trained food classification model
- `ml_models/food_scaler.pkl` - Feature scaler for food model
- `ml_models/food_encoders.pkl` - Label encoders for food model

**Performance Metrics:**
The script displays:
- ROC-AUC scores
- Classification reports (precision, recall, F1-score)
- Confusion matrices
- Feature importance rankings

**Expected Performance:**
- Diabetes Model: ROC-AUC 0.75-0.85, Accuracy 70-80%
- Food Model: Accuracy 60-70% (class imbalanced)

## Dataset Requirements

The script expects the following files in the `Datasets/` folder:

### Diabetes Dataset
- `diabetes_X_train.csv` - Training features (537 samples)
- `diabetes_y_train.csv` - Training targets
- `diabetes_X_val.csv` - Validation features (115 samples)
- `diabetes_y_val.csv` - Validation targets
- `diabetes_X_test.csv` - Test features (116 samples)
- `diabetes_y_test.csv` - Test targets
- `diabetes_scaler.pkl` - StandardScaler for features

### Food Classification Dataset
- `food_X_train.csv` - Training features (9,064 samples)
- `food_y_train.csv` - Training targets
- `food_X_val.csv` - Validation features (2,092 samples)
- `food_y_val.csv` - Validation targets
- `food_X_test.csv` - Test features (2,789 samples)
- `food_y_test.csv` - Test targets
- `food_scaler.pkl` - StandardScaler for numerical features
- `food_encoders.pkl` - Label encoders for categorical features

## Troubleshooting

### Error: Datasets directory not found
**Solution:** Ensure the `Datasets/` folder is in the project root directory (same level as `backend/`).

### Error: Missing required dataset files
**Solution:** Check that all required CSV and PKL files are present in the `Datasets/` folder.

### Error: Module not found
**Solution:** Install required dependencies:
```bash
pip install -r requirements.txt
```

### Low model performance
**Possible causes:**
- Insufficient training data
- Class imbalance (especially for food classification)
- Feature engineering needed
- Hyperparameter tuning required

**Solutions:**
- Collect more training data
- Use SMOTE for oversampling minority classes
- Add more features or feature interactions
- Perform grid search for optimal hyperparameters

## Integration

After training models, integrate them into the application:

1. **Update ML Service:**
   - Modify `app/services/diabetes_prediction_service.py` to use new model
   - Create `app/services/food_classification_service.py` for food model

2. **Test Predictions:**
   ```python
   from app.services.diabetes_prediction_service import DiabetesPredictionService
   
   service = DiabetesPredictionService(db)
   prediction, confidence, probs = service.predict(health_metrics)
   ```

3. **Deploy:**
   - Copy trained models to production server
   - Update model version in database
   - Monitor performance metrics

## Additional Resources

- See `docs/DATASET_INTEGRATION_GUIDE.md` for detailed integration instructions
- See `Datasets/README_FOR_PROGRAMMER.md` for dataset documentation
- See `backend/app/services/diabetes_prediction_service.py` for current implementation

## Future Scripts

Planned scripts for future development:
- `evaluate_model.py` - Evaluate model performance on new data
- `retrain_model.py` - Retrain model with updated data
- `export_model.py` - Export model for deployment
- `benchmark_models.py` - Compare different model architectures
