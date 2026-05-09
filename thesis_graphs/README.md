# Thesis Defense Graphs

This folder contains all visualizations for the DiaTracker thesis defense.

## How to Generate Graphs

1. Make sure you have the required Python packages:
```bash
pip install matplotlib numpy seaborn
```

2. Run the graph generation script:
```bash
cd DiaTracker/thesis_graphs
python generate_thesis_graphs.py
```

## Generated Graphs

### 1. Model Performance Comparison
- **File**: `1_model_performance_comparison.png`
- **Description**: Compares RF #1 (Glucose Predictor, R²=0.91) and RF #2 (Risk Classifier, 100% accuracy) against baseline models

### 2. Dataset Distribution
- **File**: `2_dataset_distribution.png`
- **Description**: Shows NHANES 2021-2023 dataset distribution by risk category and age groups (N=2,660)

### 3. Feature Importance - RF #1
- **File**: `3_feature_importance_rf1.png`
- **Description**: Feature importance for glucose prediction model (8 features)

### 4. Feature Importance - RF #2
- **File**: `4_feature_importance_rf2.png`
- **Description**: Feature importance for risk classification model (5 features)

### 5. Glucose Prediction Accuracy
- **File**: `5_glucose_prediction_accuracy.png`
- **Description**: Scatter plot showing actual vs predicted glucose levels with R²=0.91

### 6. Risk Classification Confusion Matrix
- **File**: `6_risk_classification_confusion_matrix.png`
- **Description**: Confusion matrix showing perfect 100% accuracy for risk classification

### 7. System Architecture
- **File**: `7_system_architecture.png`
- **Description**: Complete system architecture flowchart from data sources to end users

## Usage in Defense

These graphs are designed to be used in your PowerPoint presentation or printed for your thesis defense. All graphs are saved at 300 DPI for high-quality printing.

## Key Statistics to Mention

- **Dataset**: NHANES 2021-2023 (2,660 participants)
- **RF #1**: R²=0.91, MAE=8.5 mg/dL, RMSE=11.2 mg/dL
- **RF #2**: 100% accuracy, precision, recall, and F1-score
- **Food Database**: 200 foods with complete nutrition (Foster-Powell + USDA)
- **Training**: 80/20 train-test split, 5-fold cross-validation
