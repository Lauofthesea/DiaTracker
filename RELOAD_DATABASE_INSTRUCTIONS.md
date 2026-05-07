# Reload Database with Enriched Food Data

## Quick Instructions

### Option 1: Using Backend API (Recommended)

1. **Start the backend server:**
   ```bash
   cd DiaTracker/backend
   venv\Scripts\activate
   python main.py
   ```

2. **Call the admin endpoint:**
   - Open your browser or use curl
   - Navigate to: `http://localhost:8000/api/v1/admin/load-gi-database`
   - Or use curl:
     ```bash
     curl -X POST http://localhost:8000/api/v1/admin/load-gi-database \
       -H "Authorization: Bearer YOUR_TOKEN"
     ```

3. **Verify the reload:**
   - Check the response shows: "Successfully loaded 200 foods from enriched GI database with USDA nutritional data"
   - Search for a food in the app (e.g., "Apple juice")
   - Verify it shows real nutritional values (not 5.0g protein, 3.0g fat, 2.0g fiber)

### Option 2: Using Python Script

1. **Activate virtual environment:**
   ```bash
   cd DiaTracker/backend
   venv\Scripts\activate
   ```

2. **Run reload script:**
   ```bash
   python scripts/reload_enriched_foods.py
   ```

3. **Verify:**
   - Script should show: "✓ Loaded 200 foods with real USDA nutritional data"

### Option 3: Using PostgreSQL Directly

If you prefer to use SQL directly:

1. **Open PostgreSQL:**
   ```bash
   psql -U postgres -d ml_diabetes_tracker
   ```

2. **Check current food count:**
   ```sql
   SELECT COUNT(*) FROM foods;
   ```

3. **Use Option 1 or 2 above to reload**

## What Changed?

### Before (OLD - Hardcoded Values)
```
Apple juice:
- Calories: 46 kcal (estimated from carbs × 4)
- Protein: 5.0g ❌ HARDCODED
- Fat: 3.0g ❌ HARDCODED
- Fiber: 2.0g ❌ HARDCODED
- Carbs: 11.68g (from GI database)
```

### After (NEW - Real USDA Data)
```
Apple juice:
- Calories: 30 kcal ✅ REAL USDA DATA
- Protein: 0.0g ✅ REAL USDA DATA
- Fat: 0.0g ✅ REAL USDA DATA
- Fiber: 0.0g ✅ REAL USDA DATA
- Carbs: 7.63g ✅ REAL USDA DATA
```

## Verification Steps

### 1. Check Food Data
```bash
# In PostgreSQL
SELECT f.name, n.name as nutrient, fn.amount 
FROM foods f
JOIN food_nutrients fn ON f.food_id = fn.food_id
JOIN nutrients n ON fn.nutrient_id = n.nutrient_id
WHERE f.name = 'Apple juice'
ORDER BY n.name;
```

Expected output:
```
    name     | nutrient      | amount
-------------+---------------+--------
 Apple juice | Carbohydrate  |   7.63
 Apple juice | Energy        |  30.00
 Apple juice | Fat           |   0.00
 Apple juice | Fiber         |   0.00
 Apple juice | Protein       |   0.00
```

### 2. Test in App
1. Open DiaTracker app
2. Go to "Log Meal"
3. Search for "Apple juice"
4. Add 100g to meal
5. Check predicted glucose uses real nutritional values

### 3. Check Meal Prediction
1. Log a meal with known foods
2. Check the prediction details
3. Verify nutrients are realistic (not all 5.0g, 3.0g, 2.0g)

## Troubleshooting

### Error: "Enriched CSV not found"
- Check that `DiaTracker/datasets/gi_database_enriched.csv` exists
- If not, run the matching script again:
  ```bash
  cd DiaTracker/backend/scripts
  python match_gi_with_usda_local.py
  ```

### Error: "No module named 'sqlalchemy'"
- Make sure you activated the virtual environment:
  ```bash
  cd DiaTracker/backend
  venv\Scripts\activate
  ```

### Foods still show old values
- Database wasn't reloaded yet
- Follow Option 1 or 2 above to reload

## Status Check

Run this query to verify enriched data is loaded:

```sql
-- Check if we have realistic variety in nutrients
SELECT 
  MIN(fn.amount) as min_value,
  MAX(fn.amount) as max_value,
  AVG(fn.amount) as avg_value,
  n.name as nutrient
FROM food_nutrients fn
JOIN nutrients n ON fn.nutrient_id = n.nutrient_id
GROUP BY n.name
ORDER BY n.name;
```

Expected output (should show variety, not all same values):
```
 min_value | max_value | avg_value | nutrient
-----------+-----------+-----------+--------------
      0.00 |     83.64 |     35.21 | Carbohydrate
      0.00 |    867.00 |    245.33 | Energy
      0.00 |     93.33 |     12.45 | Fat
      0.00 |     39.50 |      5.67 | Fiber
      0.00 |     35.71 |      8.92 | Protein
```

If all values are the same (e.g., Protein always 5.0), database needs to be reloaded.

---

**Next Step**: Choose Option 1, 2, or 3 above to reload the database! ✅
