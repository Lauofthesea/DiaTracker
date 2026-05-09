"""
Convert NHANES XPT files to CSV format
Converts the 6 NHANES XPT files to individual CSV files for easier inspection
"""

import pandas as pd
from pathlib import Path

# Define paths
raw_data_dir = Path(__file__).parent.parent / "raw_data"
xpt_dir = raw_data_dir / "nhanes_2021_2023"
output_dir = raw_data_dir / "nhanes_xpt_csvs"

# Create output directory
output_dir.mkdir(exist_ok=True)

# List of NHANES files to convert
xpt_files = [
    "DEMO_L.xpt",    # Demographics
    "BMX_L.xpt",     # Body Measurements
    "GLU_L.xpt",     # Glucose Lab Results
    "DIQ_L.xpt",     # Diabetes Questionnaire
    "DR1TOT_L.xpt",  # Dietary Day 1
    "DR2TOT_L.xpt"   # Dietary Day 2
]

print("Converting NHANES XPT files to CSV...")
print("=" * 60)

for xpt_file in xpt_files:
    xpt_path = xpt_dir / xpt_file
    csv_file = xpt_file.replace('.xpt', '.csv')
    csv_path = output_dir / csv_file
    
    if not xpt_path.exists():
        print(f"⚠️  {xpt_file} not found, skipping...")
        continue
    
    try:
        # Read XPT file
        print(f"Reading {xpt_file}...")
        df = pd.read_sas(xpt_path)
        
        # Save as CSV
        df.to_csv(csv_path, index=False)
        
        print(f"✓ Converted {xpt_file} → {csv_file}")
        print(f"  Rows: {len(df):,}, Columns: {len(df.columns)}")
        
    except Exception as e:
        print(f"✗ Error converting {xpt_file}: {str(e)}")

print("=" * 60)
print(f"✓ Conversion complete!")
print(f"CSV files saved to: {output_dir}")
print(f"\nTo view the files:")
print(f"  cd {output_dir}")
print(f"  ls")
