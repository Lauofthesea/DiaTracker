# GI Database Enrichment with USDA Nutritional Data

## Problem
The Foster-Powell GI database only contains:
- GI value
- GL value  
- Serving size
- **Available carbohydrates only**

For accurate glucose predictions with RF #1 model, we need:
- ✅ Carbohydrates (from Foster-Powell)
- ❌ Protein (missing)
- ❌ Fat (missing)
- ❌ Fiber (missing)
- ❌ Accurate calories (currently estimated from carbs only)

## Solution
Cross-match Foster-Powell foods with USDA FoodData Central to get real nutritional values.

## Steps

### 1. Get USDA API Key (Recommended)
- Visit: https://fdc.nal.usda.gov/api-key-signup.html
- Sign up for a free API key
- Replace `DEMO_KEY` in `enrich_gi_with_usda.py` with your key
- **Note:** DEMO_KEY has rate limits (30 requests/hour = ~6 hours for 200 foods)

### 2. Install Dependencies
```bash
cd DiaTracker/backend/scripts
pip install -r requirements_enrichment.txt
```

### 3. Run Enrichment Script
```bash
python enrich_gi_with_usda.py
```

The script will:
1. Read `gi_database_research_only.csv`
2. For each food, search USDA FoodData Central by name
3. Use fuzzy matching to find best match
4. Extract protein, fat, fiber, and calories per 100g
5. Create `gi_database_enriched.csv` with complete data

### 4. Review Results
Open `DiaTracker/datasets/gi_database_enriched.csv` and check:
- **Matched foods:** Have USDA data (data_source = "USDA FoodData Central")
- **Unmatched foods:** Need manual research (data_source = "No USDA match - needs manual entry")

For unmatched foods:
1. Search scientific literature or USDA database manually
2. Add accurate nutritional values to the CSV
3. Update `data_source` column with reference

### 5. Update Database Loader
Modify `DiaTracker/backend/app/api/v1/endpoints/admin.py`:
- Change CSV path from `gi_database_research_only.csv` to `gi_database_enriched.csv`
- Use real nutritional values from CSV instead of hardcoded placeholders

### 6. Reload Database
```bash
# Call the admin endpoint to reload foods
curl -X POST http://localhost:8000/api/v1/admin/load-gi-database \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Expected Output
```
gi_database_enriched.csv columns:
- food_name
- gi_value
- serving_size_g
- available_carbs_g
- gl_value
- food_category
- reference
- study_details
- usda_fdc_id (NEW)
- usda_description (NEW)
- calories_per_100g (NEW - real data)
- protein_per_100g (NEW - real data)
- fat_per_100g (NEW - real data)
- fiber_per_100g (NEW - real data)
- carbohydrates_per_100g (NEW - real data)
- data_source (NEW - for thesis citation)
```

## For Thesis Defense
This approach ensures:
- ✅ GI/GL values from peer-reviewed Foster-Powell 2002 study
- ✅ Nutritional values from USDA FoodData Central (government database)
- ✅ All data sources are scientifically validated
- ✅ No estimated or placeholder values
- ✅ Proper citations for data sources

## Troubleshooting

### Rate Limit Errors
- Use your own API key instead of DEMO_KEY
- Or increase `time.sleep()` delay in the script

### Low Match Scores
- Review foods with score < 0.7
- Manually verify the USDA match is correct
- Update food name in GI database for better matching

### Missing Nutrients
- Some USDA foods may have incomplete data
- Cross-reference with other sources
- Document in `data_source` column
