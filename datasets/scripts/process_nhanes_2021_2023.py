"""
NHANES 2021-2023 Data Processing Script
========================================

Purpose: Process NHANES 2021-2023 data to prepare features for training:
- RF #1 (Glucose Predictor): 9 features
- RF #2 (Risk Classifier): 6 features

Author: DiaTracker Enhancement Project
Date: May 6, 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path

# File paths
DATA_DIR = Path(__file__).parent / "nhanes_2021_2023"
OUTPUT_DIR = Path(__file__).parent

# NHANES files
FILES = {
    'demographics': DATA_DIR / 'DEMO_L.xpt',
    'body_measures': DATA_DIR / 'BMX_L.xpt',
    'glucose': DATA_DIR / 'GLU_L.xpt',
    'diabetes_questionnaire': DATA_DIR / 'DIQ_L.xpt',
    'dietary_day1': DATA_DIR / 'DR1TOT_L.xpt',
    'dietary_day2': DATA_DIR / 'DR2TOT_L.xpt'
}


def load_xpt_files():
    """Load all NHANES XPT files."""
    print("=" * 80)
    print("STEP 1: Loading NHANES 2021-2023 XPT Files")
    print("=" * 80)
    
    data = {}
    for name, filepath in FILES.items():
        print(f"\nLoading {name}...")
        try:
            df = pd.read_sas(filepath, format='xport', encoding='utf-8')
            data[name] = df
            print(f"  ✓ Loaded {len(df)} rows, {len(df.columns)} columns")
            print(f"  Columns: {', '.join(df.columns[:10].tolist())}...")
        except Exception as e:
            print(f"  ✗ Error loading {name}: {e}")
            data[name] = None
    
    return data


def explore_data(data):
    """Explore the loaded data to understand structure."""
    print("\n" + "=" * 80)
    print("STEP 2: Exploring Data Structure")
    print("=" * 80)
    
    for name, df in data.items():
        if df is not None:
            print(f"\n{name.upper()}:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Sample data:")
            print(df.head(2))
            print(f"  Missing values:")
            print(df.isnull().sum()[df.isnull().sum() > 0])


def merge_datasets(data):
    """Merge all datasets by SEQN (participant ID)."""
    print("\n" + "=" * 80)
    print("STEP 3: Merging Datasets by SEQN (Participant ID)")
    print("=" * 80)
    
    # Start with demographics as base
    merged = data['demographics'].copy()
    print(f"\nStarting with demographics: {len(merged)} participants")
    
    # Merge each dataset
    datasets_to_merge = [
        ('body_measures', 'BMX'),
        ('glucose', 'GLU'),
        ('diabetes_questionnaire', 'DIQ'),
        ('dietary_day1', 'DR1')
    ]
    
    for name, prefix in datasets_to_merge:
        if data[name] is not None:
            before = len(merged)
            merged = merged.merge(data[name], on='SEQN', how='left', suffixes=('', f'_{prefix}'))
            after = len(merged)
            print(f"  ✓ Merged {name}: {before} → {after} participants")
    
    print(f"\nFinal merged dataset: {len(merged)} participants, {len(merged.columns)} columns")
    return merged


def extract_features(merged):
    """Extract features needed for RF #1 and RF #2."""
    print("\n" + "=" * 80)
    print("STEP 4: Extracting Features")
    print("=" * 80)
    
    # Create feature dataframe
    features = pd.DataFrame()
    features['SEQN'] = merged['SEQN']
    
    print("\n--- Demographics Features ---")
    # Age (RIDAGEYR)
    if 'RIDAGEYR' in merged.columns:
        features['age'] = merged['RIDAGEYR']
        print(f"  ✓ age: {features['age'].notna().sum()} values")
    
    # Gender (RIAGENDR: 1=Male, 2=Female)
    if 'RIAGENDR' in merged.columns:
        features['gender'] = merged['RIAGENDR'].map({1: 'Male', 2: 'Female'})
        print(f"  ✓ gender: {features['gender'].notna().sum()} values")
    
    print("\n--- Body Measures Features ---")
    # BMI (BMXBMI)
    if 'BMXBMI' in merged.columns:
        features['BMI'] = merged['BMXBMI']
        print(f"  ✓ BMI: {features['BMI'].notna().sum()} values")
    
    # Weight (BMXWT) - kg
    if 'BMXWT' in merged.columns:
        features['weight_kg'] = merged['BMXWT']
        print(f"  ✓ weight_kg: {features['weight_kg'].notna().sum()} values")
    
    # Height (BMXHT) - cm
    if 'BMXHT' in merged.columns:
        features['height_cm'] = merged['BMXHT']
        print(f"  ✓ height_cm: {features['height_cm'].notna().sum()} values")
    
    # Waist circumference (BMXWAIST) - cm (optional, for reference)
    if 'BMXWAIST' in merged.columns:
        features['waist_cm'] = merged['BMXWAIST']
        print(f"  ✓ waist_cm: {features['waist_cm'].notna().sum()} values")
    
    print("\n--- Glucose Features ---")
    # Fasting glucose (LBXGLU) - mg/dL
    if 'LBXGLU' in merged.columns:
        features['fasting_glucose'] = merged['LBXGLU']
        print(f"  ✓ fasting_glucose: {features['fasting_glucose'].notna().sum()} values")
    
    # 2-hour OGTT glucose (LBXGLT) - mg/dL
    if 'LBXGLT' in merged.columns:
        features['glucose_2hr'] = merged['LBXGLT']
        print(f"  ✓ glucose_2hr: {features['glucose_2hr'].notna().sum()} values")
    
    print("\n--- Diabetes Questionnaire Features ---")
    # Family history (DIQ180: Has any family member been told they have diabetes?)
    # DIQ180: 1=Yes, 2=No, 7=Refused, 9=Don't know
    if 'DIQ180' in merged.columns:
        features['family_history'] = merged['DIQ180'].map({1: 'Yes', 2: 'No'})
        print(f"  ✓ family_history: {features['family_history'].notna().sum()} values")
    
    # Diabetes diagnosis (DIQ010: Doctor told you have diabetes?)
    if 'DIQ010' in merged.columns:
        features['has_diabetes'] = merged['DIQ010'].map({1: 'Yes', 2: 'No', 3: 'Borderline'})
        print(f"  ✓ has_diabetes: {features['has_diabetes'].notna().sum()} values")
    
    print("\n--- Dietary Features (Day 1) ---")
    # Total carbohydrates (DR1TCARB) - g
    if 'DR1TCARB' in merged.columns:
        features['carbs_g'] = merged['DR1TCARB']
        print(f"  ✓ carbs_g: {features['carbs_g'].notna().sum()} values")
    
    # Total fiber (DR1TFIBE) - g
    if 'DR1TFIBE' in merged.columns:
        features['fiber_g'] = merged['DR1TFIBE']
        print(f"  ✓ fiber_g: {features['fiber_g'].notna().sum()} values")
    
    # Total fat (DR1TTFAT) - g
    if 'DR1TTFAT' in merged.columns:
        features['fat_g'] = merged['DR1TTFAT']
        print(f"  ✓ fat_g: {features['fat_g'].notna().sum()} values")
    
    # Total protein (DR1TPROT) - g
    if 'DR1TPROT' in merged.columns:
        features['protein_g'] = merged['DR1TPROT']
        print(f"  ✓ protein_g: {features['protein_g'].notna().sum()} values")
    
    # Total sugars (DR1TSUGR) - g
    if 'DR1TSUGR' in merged.columns:
        features['sugar_g'] = merged['DR1TSUGR']
        print(f"  ✓ sugar_g: {features['sugar_g'].notna().sum()} values")
    
    # Energy (DR1TKCAL) - kcal
    if 'DR1TKCAL' in merged.columns:
        features['energy_kcal'] = merged['DR1TKCAL']
        print(f"  ✓ energy_kcal: {features['energy_kcal'].notna().sum()} values")
    
    print(f"\nTotal features extracted: {len(features.columns) - 1}")  # -1 for SEQN
    return features


def calculate_derived_features(features):
    """Calculate derived features like available carbs and GL."""
    print("\n" + "=" * 80)
    print("STEP 5: Calculating Derived Features")
    print("=" * 80)
    
    # Available carbohydrates = total carbs - fiber
    if 'carbs_g' in features.columns and 'fiber_g' in features.columns:
        features['available_carbs_g'] = features['carbs_g'] - features['fiber_g']
        features['available_carbs_g'] = features['available_carbs_g'].clip(lower=0)
        print(f"  ✓ available_carbs_g: {features['available_carbs_g'].notna().sum()} values")
    
    # Note: GL calculation requires GI values from food database
    # For now, we'll add a placeholder column
    features['glycemic_load'] = np.nan
    print(f"  ⚠ glycemic_load: Placeholder (requires GI database merge)")
    
    # Calculate BMI if missing but weight and height available
    if 'BMI' not in features.columns or features['BMI'].isna().sum() > 0:
        if 'weight_kg' in features.columns and 'height_cm' in features.columns:
            height_m = features['height_cm'] / 100
            calculated_bmi = features['weight_kg'] / (height_m ** 2)
            if 'BMI' not in features.columns:
                features['BMI'] = calculated_bmi
            else:
                features['BMI'] = features['BMI'].fillna(calculated_bmi)
            print(f"  ✓ BMI (calculated): {features['BMI'].notna().sum()} values")
    
    return features


def classify_risk_ada_2024(features):
    """Classify diabetes risk using ADA 2024 cutoffs."""
    print("\n" + "=" * 80)
    print("STEP 6: Classifying Diabetes Risk (ADA 2024 Cutoffs)")
    print("=" * 80)
    
    def classify_row(row):
        """
        ADA 2024 Risk Classification:
        - High/Diabetes: fasting ≥126 OR 2hr ≥200 mg/dL
        - Mid/Prediabetes: fasting 100-125 OR 2hr 140-199 mg/dL
        - Low/Normal: fasting <100 AND 2hr <140 mg/dL
        """
        fasting = row.get('fasting_glucose', np.nan)
        glucose_2hr = row.get('glucose_2hr', np.nan)
        
        # High risk
        if (not pd.isna(fasting) and fasting >= 126) or \
           (not pd.isna(glucose_2hr) and glucose_2hr >= 200):
            return 'High'
        
        # Mid risk
        if (not pd.isna(fasting) and 100 <= fasting < 126) or \
           (not pd.isna(glucose_2hr) and 140 <= glucose_2hr < 200):
            return 'Mid'
        
        # Low risk
        if (not pd.isna(fasting) and fasting < 100) and \
           (pd.isna(glucose_2hr) or glucose_2hr < 140):
            return 'Low'
        
        return np.nan
    
    features['risk_level'] = features.apply(classify_row, axis=1)
    
    # Print distribution
    risk_counts = features['risk_level'].value_counts()
    print(f"\nRisk Level Distribution:")
    for level in ['Low', 'Mid', 'High']:
        count = risk_counts.get(level, 0)
        pct = (count / len(features) * 100) if len(features) > 0 else 0
        print(f"  {level}: {count} ({pct:.1f}%)")
    
    missing = features['risk_level'].isna().sum()
    print(f"  Missing: {missing} ({missing/len(features)*100:.1f}%)")
    
    return features


def clean_data(features):
    """Clean data by removing invalid values and outliers."""
    print("\n" + "=" * 80)
    print("STEP 7: Cleaning Data")
    print("=" * 80)
    
    initial_count = len(features)
    print(f"\nInitial sample size: {initial_count}")
    
    # Remove participants with missing critical features
    critical_features = ['age', 'gender', 'BMI', 'fasting_glucose']
    
    print(f"\nRemoving rows with missing critical features:")
    for feature in critical_features:
        if feature in features.columns:
            before = len(features)
            features = features[features[feature].notna()]
            removed = before - len(features)
            if removed > 0:
                print(f"  - {feature}: removed {removed} rows")
    
    # Age filter: 18-70 years (adult population)
    if 'age' in features.columns:
        before = len(features)
        features = features[(features['age'] >= 18) & (features['age'] <= 70)]
        removed = before - len(features)
        print(f"  - Age filter (18-70): removed {removed} rows")
    
    # BMI filter: 15-60 (remove extreme outliers)
    if 'BMI' in features.columns:
        before = len(features)
        features = features[(features['BMI'] >= 15) & (features['BMI'] <= 60)]
        removed = before - len(features)
        print(f"  - BMI filter (15-60): removed {removed} rows")
    
    # Glucose filter: 50-400 mg/dL (remove measurement errors)
    if 'fasting_glucose' in features.columns:
        before = len(features)
        features = features[(features['fasting_glucose'] >= 50) & 
                           (features['fasting_glucose'] <= 400)]
        removed = before - len(features)
        print(f"  - Glucose filter (50-400): removed {removed} rows")
    
    final_count = len(features)
    print(f"\nFinal sample size: {final_count}")
    print(f"Total removed: {initial_count - final_count} ({(initial_count - final_count)/initial_count*100:.1f}%)")
    
    return features


def generate_summary_statistics(features):
    """Generate summary statistics for the processed data."""
    print("\n" + "=" * 80)
    print("STEP 8: Summary Statistics")
    print("=" * 80)
    
    numeric_cols = features.select_dtypes(include=[np.number]).columns
    
    print("\nNumeric Features Summary:")
    summary = features[numeric_cols].describe()
    print(summary.round(2))
    
    print("\nCategorical Features Summary:")
    categorical_cols = ['gender', 'family_history', 'has_diabetes', 'risk_level']
    for col in categorical_cols:
        if col in features.columns:
            print(f"\n{col}:")
            print(features[col].value_counts())
    
    # Missing data summary
    print("\nMissing Data Summary:")
    missing = features.isnull().sum()
    missing_pct = (missing / len(features) * 100).round(1)
    missing_df = pd.DataFrame({
        'Missing Count': missing,
        'Missing %': missing_pct
    })
    missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
    if len(missing_df) > 0:
        print(missing_df)
    else:
        print("  No missing data!")


def save_processed_data(features):
    """Save processed data to CSV."""
    print("\n" + "=" * 80)
    print("STEP 9: Saving Processed Data")
    print("=" * 80)
    
    output_file = OUTPUT_DIR / "nhanes_2021_2023_processed.csv"
    features.to_csv(output_file, index=False)
    print(f"\n✓ Saved processed data to: {output_file}")
    print(f"  Rows: {len(features)}")
    print(f"  Columns: {len(features.columns)}")
    
    # Save data dictionary
    dict_file = OUTPUT_DIR / "nhanes_2021_2023_data_dictionary.txt"
    with open(dict_file, 'w') as f:
        f.write("NHANES 2021-2023 Processed Data Dictionary\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total Participants: {len(features)}\n")
        f.write(f"Total Features: {len(features.columns)}\n\n")
        f.write("Features:\n")
        f.write("-" * 80 + "\n")
        for col in features.columns:
            dtype = features[col].dtype
            non_null = features[col].notna().sum()
            null = features[col].isna().sum()
            f.write(f"\n{col}:\n")
            f.write(f"  Type: {dtype}\n")
            f.write(f"  Non-null: {non_null} ({non_null/len(features)*100:.1f}%)\n")
            f.write(f"  Null: {null} ({null/len(features)*100:.1f}%)\n")
            if dtype in ['int64', 'float64']:
                f.write(f"  Min: {features[col].min()}\n")
                f.write(f"  Max: {features[col].max()}\n")
                f.write(f"  Mean: {features[col].mean():.2f}\n")
                f.write(f"  Median: {features[col].median():.2f}\n")
    
    print(f"✓ Saved data dictionary to: {dict_file}")


def main():
    """Main processing pipeline."""
    print("\n" + "=" * 80)
    print("NHANES 2021-2023 DATA PROCESSING PIPELINE")
    print("=" * 80)
    print("\nThis script will:")
    print("  1. Load 6 NHANES XPT files")
    print("  2. Explore data structure")
    print("  3. Merge datasets by participant ID (SEQN)")
    print("  4. Extract features for RF #1 and RF #2")
    print("  5. Calculate derived features")
    print("  6. Classify diabetes risk (ADA 2024)")
    print("  7. Clean data (remove outliers, missing values)")
    print("  8. Generate summary statistics")
    print("  9. Save processed data to CSV")
    print("\n" + "=" * 80)
    
    try:
        # Load data
        data = load_xpt_files()
        
        # Explore data structure
        explore_data(data)
        
        # Merge datasets
        merged = merge_datasets(data)
        
        # Extract features
        features = extract_features(merged)
        
        # Calculate derived features
        features = calculate_derived_features(features)
        
        # Classify risk
        features = classify_risk_ada_2024(features)
        
        # Clean data
        features = clean_data(features)
        
        # Generate summary statistics
        generate_summary_statistics(features)
        
        # Save processed data
        save_processed_data(features)
        
        print("\n" + "=" * 80)
        print("✓ PROCESSING COMPLETE!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Review: nhanes_2021_2023_processed.csv")
        print("  2. Review: nhanes_2021_2023_data_dictionary.txt")
        print("  3. Merge with GI/GL database to calculate glycemic_load")
        print("  4. Train RF #1 (Glucose Predictor)")
        print("  5. Train RF #2 (Risk Classifier)")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
