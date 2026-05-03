Data Delivery Summary
Machine Learning Datasets for Diabetes Support System

Prepared by: Data Engineering Team  
Date: April 29, 2026  
For: Programming Team  
Project: Machine Learning-Based Calorie Calculator for Diabetes Support


Mission Accomplished

TWO DATASETS PREPARED AND READY FOR ML DEVELOPMENT

Dataset 1: Pima Indians Diabetes Dataset
Source: Pima Indians Diabetes Database
Total Samples: 768 patients
Purpose: Predict diabetes in patients
Features: 8 medical measurements
Target: Binary (Has Diabetes / No Diabetes)
Status: Cleaned, scaled, split (train/val/test)

Dataset 2: USDA Food Nutrition Dataset
Source: USDA FoodData Central (December 2025)
Total Samples: 13,945 foods (from 2M+ available)
Purpose: Classify foods by diabetes risk level
Features: 10 nutritional and categorical features
Target: 3 classes (Low Risk / Medium Risk / High Risk)
Status: Cleaned, scaled, encoded, split (train/val/test)




DATASET 1: Pima Indians Diabetes Dataset

Purpose
Predict whether a patient has diabetes based on diagnostic measurements.

Dataset Statistics

Total Samples: 768 patients
Training: 537 samples (69.9%)
Validation: 115 samples (15.0%)
Test: 116 samples (15.1%)
Features: 8 medical measurements
Target: Binary classification

Class Distribution

No Diabetes (0): 500 patients (65.1%)
Has Diabetes (1): 268 patients (34.9%)

Features (8 total)

All features are scaled (mean=0, std=1):

1. Pregnancies - Number of times pregnant
2. Glucose - Plasma glucose concentration (mg/dL)
3. BloodPressure - Diastolic blood pressure (mm Hg)
4. SkinThickness - Triceps skin fold thickness (mm)
5. Insulin - 2-Hour serum insulin (mu U/ml)
6. BMI - Body mass index
7. DiabetesPedigreeFunction - Genetic diabetes influence
8. Age - Age in years

Files Included (7 files)

diabetes_X_train.csv - Training features (537 samples)
diabetes_y_train.csv - Training targets
diabetes_X_val.csv - Validation features (115 samples)
diabetes_y_val.csv - Validation targets
diabetes_X_test.csv - Test features (116 samples)
diabetes_y_test.csv - Test targets
diabetes_scaler.pkl - StandardScaler for features
diabetes_feature_names.txt - List of 8 feature names




DATASET 2: USDA Food Nutrition Dataset

Purpose
Classify foods by diabetes risk level for dietary recommendations.

Dataset Statistics

Total Samples: 13,945 foods
Training: 9,064 samples (65.0%)
Validation: 2,092 samples (15.0%)
Test: 2,789 samples (20.0%)
Features: 10 (7 nutritional + 3 categorical)
Target: 3-class classification

Class Distribution

Medium Risk: 8,326 samples (56.4%) - Moderate nutritional profile
High Risk: 5,505 samples (37.3%) - High carbs/sugar, low fiber
Low Risk: 114 samples (0.8%) - Low carbs/sugar, high fiber

Classification Rules

High Risk: Carbs greater than 60g OR Sugar greater than 20g OR (Carbs greater than 30g AND Fiber less than 3g)
Low Risk: Carbs less than 15g AND Sugar less than 5g AND Fiber greater than 5g
Medium Risk: Everything else

Features (10 total)

Nutritional Features (7) - All scaled (mean=0, std=1)
carbs_total - Total carbohydrates (g)
calories - Energy content (kcal)
fiber - Dietary fiber (g)
protein - Protein content (g)
fat_total - Total fat (g)
sugars_total - Total sugars (g)
sodium - Sodium content (mg)

Categorical Features (3) - All encoded (0,1,2...)
data_type - Food data type (foundation, branded, etc.)
category_code - USDA food category code
food_category - Food category description

Files Included (9 files)

food_X_train.csv - Training features (9,064 samples)
food_y_train.csv - Training targets
food_X_val.csv - Validation features (2,092 samples)
food_y_val.csv - Validation targets
food_X_test.csv - Test features (2,789 samples)
food_y_test.csv - Test targets
food_encoders.pkl - Label encoders for categorical variables
food_scaler.pkl - StandardScaler for numerical features
food_feature_names.txt - List of feature column names




Important Notes for Programmer

Dataset 1: Diabetes Prediction
Relatively balanced classes (65% vs 35%)
All features are numerical
Focus on ROC-AUC and precision/recall
Medical data - interpretability is important
Recommended models: Logistic Regression, Random Forest, XGBoost

Dataset 2: Food Classification
SEVERE CLASS IMBALANCE (Low Risk only 0.8%)
Must use class balancing techniques:
  class_weight='balanced' in sklearn models
  SMOTE oversampling
  Stratified cross-validation
Don't use accuracy alone (misleading with imbalanced data)
Use F1-Score, Precision, Recall per class
Recommended models: Random Forest with class_weight, XGBoost

Evaluation Metrics

For Diabetes Prediction:
ROC-AUC Score
Precision and Recall
F1-Score
Confusion Matrix
Sensitivity and Specificity

For Food Classification:
F1-Score (weighted and macro)
Precision and Recall per class
Confusion Matrix
ROC-AUC (one-vs-rest)




Quick Start Code

DIABETES PREDICTION MODEL

import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score

Load diabetes data
diabetes_X_train = pd.read_csv('diabetes_X_train.csv')
diabetes_y_train = pd.read_csv('diabetes_y_train.csv')['Outcome']
diabetes_X_val = pd.read_csv('diabetes_X_val.csv')
diabetes_y_val = pd.read_csv('diabetes_y_val.csv')['Outcome']

Train model
diabetes_model = RandomForestClassifier(n_estimators=100, random_state=42)
diabetes_model.fit(diabetes_X_train, diabetes_y_train)

Evaluate
diabetes_pred = diabetes_model.predict(diabetes_X_val)
print("ROC-AUC:", roc_auc_score(diabetes_y_val, diabetes_pred))
print(classification_report(diabetes_y_val, diabetes_pred))


FOOD CLASSIFICATION MODEL

Load food data
food_X_train = pd.read_csv('food_X_train.csv')
food_y_train = pd.read_csv('food_y_train.csv')['target']
food_X_val = pd.read_csv('food_X_val.csv')
food_y_val = pd.read_csv('food_y_val.csv')['target']

Load encoders
with open('food_encoders.pkl', 'rb') as f:
    food_encoders = pickle.load(f)

Train model (handles class imbalance)
food_model = RandomForestClassifier(
    n_estimators=100,
    class_weight='balanced',
    random_state=42
)
food_model.fit(food_X_train, food_y_train)

Evaluate
food_pred = food_model.predict(food_X_val)
print(classification_report(food_y_val, food_pred, 
                          target_names=food_encoders['target'].classes_))




Data Quality Assurance

Dataset 1: Diabetes
Missing values handled (zeros replaced with median)
All features standardized (mean=0, std=1)
Stratified splits preserve class distribution
No data leakage

Dataset 2: Food
No missing values (NaN filled with 0)
Numerical features standardized (mean=0, std=1)
Categorical features label encoded
Stratified splits preserve class distribution
No data leakage




Expected Performance

Dataset 1: Diabetes Prediction
Baseline Accuracy: approximately 65% (majority class)
Target ROC-AUC: 0.75-0.85
Focus: Sensitivity (detecting diabetes cases)

Dataset 2: Food Classification
Baseline Accuracy: approximately 56% (majority class)
Target F1-Score: 0.70-0.80 (with proper class balancing)
Challenge: Low Risk class detection (only 0.8% of data)
Focus: Precision/Recall for High Risk foods




Complete File List

Total Files: 28

DIABETES DATASET (7 files)
diabetes_X_train.csv
diabetes_y_train.csv
diabetes_X_val.csv
diabetes_y_val.csv
diabetes_X_test.csv
diabetes_y_test.csv
diabetes_scaler.pkl
diabetes_feature_names.txt

FOOD DATASET (9 files)
food_X_train.csv
food_y_train.csv
food_X_val.csv
food_y_val.csv
food_X_test.csv
food_y_test.csv
food_encoders.pkl
food_scaler.pkl
food_feature_names.txt

CHARTS (7 files)
01_diabetes_risk_distribution.png
02_feature_correlation_heatmap.png
03_nutritional_features_distribution.png
04_train_val_test_split.png
05_class_distribution_by_split.png
06_feature_importance_simulation.png
07_data_quality_summary.png

DOCUMENTATION (5 files)
README_FOR_PROGRAMMER.md
DATA_DELIVERY_SUMMARY_CLEAN.md (this file)
CHART_INDEX.md
requirements_preprocessing.txt




System Integration

How the Two Datasets Work Together

1. Diabetes Prediction (Dataset 1)
   Input: Patient medical measurements
   Output: Diabetes risk prediction (Yes/No)
   Use: Identify patients who need dietary support

2. Food Classification (Dataset 2)
   Input: Food nutritional information
   Output: Diabetes risk level of food (Low/Medium/High)
   Use: Recommend appropriate foods based on diabetes status

3. Complete System
   Predict if patient has diabetes
   Recommend foods based on their diabetes status
   Track calories and nutritional intake
   Provide dietary guidance




Next Steps for Programmer

1. Load and explore both datasets
2. Train baseline models for both tasks
3. Implement class balancing for food classification
4. Tune hyperparameters using validation sets
5. Evaluate on test sets with proper metrics
6. Build prediction API for both models
7. Create web interface for diabetes support system
8. Integrate both models into complete system




Connection to Project Requirements

This delivery supports the "Machine Learning-Based Calorie Calculator for Diabetes Support" project:

Diabetes Focus: Dataset 1 predicts diabetes, Dataset 2 classifies food risk
Nutritional Data: Calories, carbs, sugar, fiber - all key diabetes metrics
Large Scale: 768 patients + 13,945 foods
Real-world Data: Medical database + USDA authoritative source
ML Ready: Both datasets preprocessed and split for immediate development




Support

If the programmer needs:
More data: Can process additional samples
Different features: Can extract other measurements/nutrients
Different targets: Can create other classification schemes
Data issues: Contact data engineering team


Data Engineering Mission Complete
Two Datasets Delivered
Ready for ML Development Phase
