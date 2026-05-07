# NHANES 2021-2023 Processing Summary

**Date**: May 6, 2026  
**Status**: ✅ Successfully Processed

---

## Processing Results

### Input Data
- **Total participants**: 11,933
- **Source files**: 6 XPT files
  - DEMO_L.xpt (Demographics)
  - BMX_L.xpt (Body Measures)
  - GLU_L.xpt (Glucose Lab)
  - DIQ_L.xpt (Diabetes Questionnaire)
  - DR1TOT_L.xpt (Dietary Day 1)
  - DR2TOT_L.xpt (Dietary Day 2)

### Output Data
- **Final sample size**: **2,660 participants**
- **Features extracted**: 18 features
- **Output file**: `nhanes_2021_2023_processed.csv`

---

## Sample Characteristics

### Demographics
- **Age**: 18-70 years (mean: 47.9 ± 15.7 years)
- **Gender**: 
  - Female: 1,485 (55.8%)
  - Male: 1,175 (44.2%)

### Body Measures
- **BMI**: 15-60 kg/m² (mean: 29.5 ± 7.1 kg/m²)
- **Weight**: mean 82.4 ± 21.3 kg
- **Height**: mean 167.1 ± 10.2 cm
- **Waist circumference**: mean 99.8 ± 16.5 cm

### Glucose Measures
- **Fasting glucose**: 50-400 mg/dL (mean: 106.3 ± 28.4 mg/dL)
- **2-hour OGTT**: Not available in this dataset

### Diabetes Status
- **No diabetes**: 2,254 (84.7%)
- **Has diabetes**: 311 (11.7%)
- **Borderline**: 94 (3.5%)

### Risk Classification (ADA 2024)
- **Low Risk**: 1,285 (48.3%)
- **Mid Risk**: 1,074 (40.4%)
- **High Risk**: 301 (11.3%)

### Dietary Intake (Day 1)
- **Total carbs**: mean 212.1 ± 113.6 g
- **Available carbs**: mean 212.1 ± 113.6 g
- **Fiber**: mean 16.8 ± 10.2 g
- **Fat**: mean 77.3 ± 48.5 g
- **Protein**: mean 78.9 ± 45.2 g
- **Sugar**: mean 95.4 ± 68.7 g
- **Energy**: mean 1,989 ± 1,012 kcal

---

## Data Cleaning Steps

### Exclusion Criteria
1. **Missing critical features**: 
   - Missing BMI: 3,462 removed
   - Missing fasting glucose: 4,845 removed
2. **Age filter** (18-70 years): 944 removed
3. **BMI filter** (15-60 kg/m²): 19 removed
4. **Glucose filter** (50-400 mg/dL): 3 removed

**Total removed**: 9,273 participants (77.7%)

---

## Features Extracted

### For RF #1 (Glucose Predictor) - 9 features
1. `fasting_glucose` (mg/dL) - ✅ Complete
2. `glycemic_load` (GL) - ⚠️ **PENDING** (requires GI database merge)
3. `fat_g` (g) - ✅ 78.7% complete
4. `protein_g` (g) - ✅ 78.7% complete
5. `fiber_g` (g) - ✅ 78.7% complete
6. `BMI` (kg/m²) - ✅ Complete
7. `age` (years) - ✅ Complete
8. `gender` (Male/Female) - ✅ Complete
9. `meal_type` (breakfast/lunch/dinner) - ⚠️ **NOT AVAILABLE** in NHANES

### For RF #2 (Risk Classifier) - 6 features
1. `fasting_glucose` (mg/dL) - ✅ Complete
2. `glucose_1hr` (mg/dL) - ⚠️ **NOT AVAILABLE** (will be predicted by RF #1)
3. `BMI` (kg/m²) - ✅ Complete
4. `age` (years) - ✅ Complete
5. `gender` (Male/Female) - ✅ Complete
6. `family_history` (Yes/No) - ⚠️ **NOT AVAILABLE** in NHANES 2021-2023

---

## Missing Data Summary

| Feature | Missing Count | Missing % |
|---------|--------------|-----------|
| `glycemic_load` | 2,660 | 100.0% |
| `carbs_g` | 566 | 21.3% |
| `fiber_g` | 566 | 21.3% |
| `fat_g` | 566 | 21.3% |
| `protein_g` | 566 | 21.3% |
| `sugar_g` | 566 | 21.3% |
| `energy_kcal` | 566 | 21.3% |
| `available_carbs_g` | 566 | 21.3% |
| `waist_cm` | 83 | 3.1% |
| `has_diabetes` | 1 | 0.0% |

---

## Critical Issues Identified

### 1. ⚠️ **Glycemic Load (GL) - 100% Missing**
**Problem**: GL calculation requires GI values from food database  
**Solution**: 
- Merge NHANES dietary data with GI/GL database (200 foods)
- For unmatched foods, use category-based GI averages
- Formula: `GL = (available_carbs_g × GI) / 100`

### 2. ⚠️ **Family History - Not Available**
**Problem**: DIQ175A (family history) column not found in NHANES 2021-2023  
**Solution Options**:
- **Option A**: Remove family_history from RF #2 (reduce to 5 features)
- **Option B**: Use alternative NHANES cycles (2017-2020) that have this variable
- **Option C**: Impute based on diabetes prevalence statistics

### 3. ⚠️ **Meal Type - Not Available**
**Problem**: NHANES doesn't record meal type (breakfast/lunch/dinner)  
**Solution Options**:
- **Option A**: Remove meal_type from RF #1 (reduce to 8 features)
- **Option B**: Use time of day as proxy (DR1DBIH - time of first meal)
- **Option C**: Assume all meals are "mixed" (average effect)

### 4. ⚠️ **1-Hour Glucose - Not Available**
**Problem**: NHANES only has fasting glucose, not 1-hour post-meal  
**Solution**: This is expected - RF #1 will predict glucose_1hr from meal composition

### 5. ⚠️ **Dietary Data - 21.3% Missing**
**Problem**: 566 participants missing dietary intake data  
**Impact**: Can only train RF #1 on 2,094 participants (78.7%)  
**Solution**: This is acceptable - still have 2,000+ samples for training

---

## Next Steps

### Immediate Actions Required

#### 1. **Merge GI/GL Database** (CRITICAL)
Create script to:
- Load `gi_database_research_only.csv` (200 foods)
- Match NHANES food codes to GI database
- Calculate GL for each participant
- Handle unmatched foods (category-based GI)

#### 2. **Handle Missing Features**
Decide on:
- **family_history**: Remove or impute?
- **meal_type**: Remove or use time proxy?

#### 3. **Create Training Datasets**
Split data into:
- **RF #1 training set**: Participants with complete dietary + glucose data (~2,094)
- **RF #2 training set**: All participants with glucose + BMI + demographics (2,660)
- **Train/test split**: 80/20 or 70/30

#### 4. **Train Models**
- Train RF #1 (Glucose Predictor)
- Train RF #2 (Risk Classifier)
- Validate performance

---

## Revised Model Architecture

### Option A: Simplified (Recommended)

**RF #1 (Glucose Predictor) - 8 features** (remove meal_type):
1. fasting_glucose
2. glycemic_load
3. fat_g
4. protein_g
5. fiber_g
6. BMI
7. age
8. gender

**RF #2 (Risk Classifier) - 5 features** (remove family_history):
1. fasting_glucose
2. glucose_1hr (from RF #1)
3. BMI
4. age
5. gender

### Option B: Use Time Proxy

**RF #1 (Glucose Predictor) - 9 features** (use time as meal_type proxy):
1. fasting_glucose
2. glycemic_load
3. fat_g
4. protein_g
5. fiber_g
6. BMI
7. age
8. gender
9. meal_time (derived from DR1DBIH)

**RF #2 (Risk Classifier) - 5 features** (same as Option A)

---

## Files Generated

1. **nhanes_2021_2023_processed.csv** (2,660 rows × 18 columns)
   - Clean, processed data ready for model training
   
2. **nhanes_2021_2023_data_dictionary.txt**
   - Complete data dictionary with feature descriptions

3. **process_nhanes_2021_2023.py**
   - Reusable processing script

---

## Citations for Thesis

**Dataset Citation**:
> Centers for Disease Control and Prevention (CDC). National Health and Nutrition Examination Survey (NHANES) 2021-2023. National Center for Health Statistics (NCHS). Available from: https://wwwn.cdc.gov/nchs/nhanes/

**Risk Classification Citation**:
> American Diabetes Association. 2024. Standards of Care in Diabetes—2024. *Diabetes Care* 47(Suppl 1):S20-S42. Table 2.1.

---

**Last Updated**: May 6, 2026  
**Status**: Ready for GI/GL merge and model training
