# Datasets Currently In Use

**Last Updated**: May 6, 2026  
**Status**: Active Development

---

## Primary Datasets

### 1. NHANES 2021-2023 (Processed) ✅
**File**: `new_datasets/nhanes_2021_2023_processed.csv`

**Purpose**: Training data for RF #1 (Glucose Predictor) and RF #2 (Risk Classifier)

**Details**:
- **Participants**: 2,660 (after cleaning)
- **Age range**: 18-70 years
- **Features**: 18 features extracted
- **Source**: CDC National Health and Nutrition Examination Survey

**Risk Distribution**:
- Low Risk: 1,285 (48.3%)
- Mid Risk: 1,074 (40.4%)
- High Risk: 301 (11.3%)

**Citation**:
> Centers for Disease Control and Prevention (CDC). 2023. National Health and Nutrition Examination Survey (NHANES) 2021-2023. National Center for Health Statistics (NCHS).

---

### 2. GI/GL Database (Research-Only) ✅
**File**: `gi_database_research_only.csv`

**Purpose**: Calculate glycemic load for meals

**Details**:
- **Foods**: 200 peer-reviewed foods
- **Sources**: Foster-Powell 2002, Atkinson 2021
- **Quality**: All tested in humans, NO estimated values
- **Includes**: food_name, gi_value, serving_size_g, available_carbs_g, gl_value, food_category, reference, study_details

**Food Categories**:
- Bakery Products (breads, muffins, cakes)
- Cereal Grains (rice, barley, quinoa)
- Breakfast Cereals
- Pasta & Noodles
- Fruits & Fruit Juices
- Legumes (beans, lentils)
- Vegetables (potatoes, carrots, etc.)
- Dairy Products
- Snacks & Confectionery
- Sugars & Syrups

**Citations**:
> Foster-Powell K, Holt SHA, Brand-Miller JC. 2002. International table of glycemic index and glycemic load values: 2002. Am J Clin Nutr 76(1):5-56.

> Atkinson FS, Brand-Miller JC, Foster-Powell K, Buyken AE, Goletzke J. 2021. International tables of glycemic index and glycemic load values 2021. Am J Clin Nutr 114(5):1625-1632.

---

### 3. USDA Food Database ✅
**File**: `food_lookup_database.csv`

**Purpose**: Nutrient composition lookup (carbs, fiber, fat, protein)

**Details**:
- **Foods**: 343,877 foods
- **Source**: USDA FoodData Central
- **Includes**: Detailed nutrient composition for meal calculations

**Citation**:
> USDA. 2024. FoodData Central. U.S. Department of Agriculture.

---

## Supporting Files

### Documentation
- `ENHANCEMENT_PLAN.md` - Complete project plan
- `NHANES_PROCESSING_SUMMARY.md` - NHANES processing details
- `SESSION_SUMMARY.md` - Development progress
- `DATASETS_IN_USE.md` - This file
- `new_datasets/nhanes_2021_2023_data_dictionary.txt` - NHANES data dictionary

### Scripts
- `new_datasets/process_nhanes_2021_2023.py` - NHANES processing script

---

## Removed/Unused Datasets

The following files were removed as they are not needed for the current implementation:

### ❌ Removed GI Databases
1. `gi_database_starter.csv` - Initial version (60 foods, too small)
2. `gi_database_foster_powell_2002.csv` - Partial extract (170 foods, superseded)
3. `gi_database_comprehensive.csv` - Had estimated values (not peer-reviewed)

**Reason**: Using `gi_database_research_only.csv` (200 peer-reviewed foods) is sufficient and meets thesis defense requirements (no estimated values).

---

## Future Expansion (Optional)

### Atkinson 2021 Supplementary Data
- **Foods**: 4,650 with GI + GL
- **Access**: Requires university library subscription
- **Status**: Can be added later without affecting current work
- **DOI**: 10.1093/ajcn/nqab233

### Panlasigui 2006 (Filipino Foods)
- **Foods**: 50 Filipino foods with GI + GL
- **Citation**: Panlasigui LN, Thompson LU. 2006. Glycemic index of some Filipino foods. Asia Pac J Clin Nutr 15(1):97-101.

---

## Model Training Datasets

### RF #1 (Glucose Predictor)
**Training Data**: NHANES participants with complete dietary data
- **Sample size**: ~2,094 participants (78.7% of total)
- **Features**: 8 features
  1. fasting_glucose
  2. glycemic_load (calculated from GI database)
  3. fat_g
  4. protein_g
  5. fiber_g
  6. BMI
  7. age
  8. gender

### RF #2 (Risk Classifier)
**Training Data**: All NHANES participants with glucose + demographics
- **Sample size**: 2,660 participants (100%)
- **Features**: 5 features
  1. fasting_glucose
  2. glucose_1hr (predicted by RF #1)
  3. BMI
  4. age
  5. gender

---

## Data Quality Standards

### Inclusion Criteria
✅ Peer-reviewed sources only  
✅ Tested in human subjects  
✅ Complete data (no missing critical features)  
✅ Age 18-70 years  
✅ BMI 15-60 kg/m²  
✅ Glucose 50-400 mg/dL  

### Exclusion Criteria
❌ Estimated GI values  
❌ Missing fasting glucose  
❌ Missing BMI  
❌ Extreme outliers  

---

## Algorithm: Random Forest

**Model Type**: Random Forest (Ensemble Learning)

**RF #1**: Random Forest Regressor (predicts continuous glucose values)  
**RF #2**: Random Forest Classifier (classifies Low/Mid/High risk)

**Citation**:
> Breiman L. 2001. Random Forests. Machine Learning 45(1):5-32.

**Advantages**:
- Handles non-linear relationships
- Robust to outliers
- Feature importance analysis
- No need for feature scaling
- Handles missing values well
- Reduces overfitting through ensemble

---

## Next Steps

1. ✅ NHANES data processed
2. ✅ GI/GL database selected (200 foods)
3. ⚠️ **NEXT**: Merge GI/GL with NHANES dietary data
4. ⚠️ Calculate glycemic_load for each participant
5. ⚠️ Split train/test sets
6. ⚠️ Train RF #1 (Glucose Predictor)
7. ⚠️ Train RF #2 (Risk Classifier)

---

**Status**: Phase 1 (Data Preparation) - 60% Complete  
**Model**: Random Forest (RF #1 Regressor + RF #2 Classifier)  
**Ready for**: GI/GL merge and model training
