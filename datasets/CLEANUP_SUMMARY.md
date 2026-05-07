# Dataset Cleanup Summary

**Date**: May 6, 2026  
**Action**: Removed unused GI/GL database files

---

## Files Removed ❌

### 1. `gi_database_starter.csv`
- **Size**: 60 foods
- **Reason**: Too small, initial test version
- **Status**: Superseded by `gi_database_research_only.csv`

### 2. `gi_database_foster_powell_2002.csv`
- **Size**: 170 foods
- **Reason**: Partial extract, incomplete
- **Status**: Superseded by `gi_database_research_only.csv`

### 3. `gi_database_comprehensive.csv`
- **Size**: 400+ foods
- **Reason**: Contained estimated GI values (not peer-reviewed)
- **Status**: Rejected - thesis defense requires only tested values

---

## Files Kept ✅

### `gi_database_research_only.csv`
- **Size**: 200 foods
- **Quality**: 100% peer-reviewed, tested in humans
- **Sources**: Foster-Powell 2002, Atkinson 2021
- **Status**: ACTIVE - Used for glycemic load calculations

**Why this file?**
- All values tested in human subjects
- No estimated or calculated values
- Proper citations for thesis defense
- Sufficient coverage of common foods
- Can be expanded later if needed

---

## Current Dataset Structure

```
DiaTracker/datasets/
├── gi_database_research_only.csv          ✅ ACTIVE (200 foods)
├── food_lookup_database.csv               ✅ ACTIVE (343,877 foods)
├── new_datasets/
│   ├── nhanes_2021_2023_processed.csv    ✅ ACTIVE (2,660 participants)
│   ├── nhanes_2021_2023/                 ✅ ACTIVE (6 XPT files)
│   └── process_nhanes_2021_2023.py       ✅ ACTIVE (processing script)
└── [documentation files]                  ✅ ACTIVE
```

---

## Model Confirmation

**Algorithm**: Random Forest (RF)

**RF #1**: Random Forest Regressor
- Predicts glucose_1hr (continuous value)
- 8 input features
- Output: mg/dL

**RF #2**: Random Forest Classifier  
- Classifies risk level (Low/Mid/High)
- 5 input features
- Output: categorical (3 classes)

**Citation**: Breiman L. 2001. Random Forests. Machine Learning 45(1):5-32.

---

## Impact Assessment

### Before Cleanup
- 4 GI/GL database files (confusing)
- Unclear which file to use
- Some files had estimated values (not suitable for thesis)

### After Cleanup
- 1 GI/GL database file (clear)
- 100% peer-reviewed values
- Ready for thesis defense
- Cleaner project structure

### No Functionality Lost
- All 200 peer-reviewed foods retained
- Can expand database later if needed
- Processing scripts unchanged
- NHANES data unaffected

---

## Next Steps

1. ✅ Cleanup complete
2. ✅ Using Random Forest confirmed
3. ⚠️ **NEXT**: Merge `gi_database_research_only.csv` with NHANES dietary data
4. ⚠️ Calculate glycemic_load for each participant
5. ⚠️ Train RF #1 and RF #2 models

---

**Status**: Cleanup Complete ✅  
**Active Datasets**: 3 (NHANES, GI/GL, USDA)  
**Model**: Random Forest (Confirmed)  
**Ready for**: GI/GL merge and model training
