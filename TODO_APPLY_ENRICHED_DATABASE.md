# TODO: Apply Enriched Food Database

**Date**: May 7, 2026  
**Priority**: HIGH - Required for accurate predictions

---

## Quick Checklist

### ✅ COMPLETED
- [x] Cross-matched GI database with USDA (200 foods, 100% match rate)
- [x] Manually verified 27 low-confidence matches
- [x] Updated `admin.py` to use enriched CSV
- [x] Fixed frontend date format issue in `foodApi.ts`
- [x] Created reload scripts
- [x] Created documentation

### ⏳ TO DO (15 minutes)

#### 1. Reload Database (5 minutes)
- [ ] **Start backend server**
  ```bash
  cd DiaTracker/backend
  venv\Scripts\activate
  python main.py
  ```

- [ ] **Call admin endpoint** (choose one):
  - **Option A**: Open browser → `http://localhost:8000/api/v1/admin/load-gi-database`
  - **Option B**: Use curl:
    ```bash
    curl -X POST http://localhost:8000/api/v1/admin/load-gi-database
    ```
  - **Option C**: Run script:
    ```bash
    python scripts/reload_enriched_foods.py
    ```

- [ ] **Verify success message**:
  - Should see: "Successfully loaded 200 foods from enriched GI database with USDA nutritional data"

#### 2. Verify Database (3 minutes)
- [ ] **Check in PostgreSQL**:
  ```bash
  psql -U postgres -d ml_diabetes_tracker
  ```
  ```sql
  -- Check Apple juice has real values (not 5.0, 3.0, 2.0)
  SELECT f.name, n.name as nutrient, fn.amount 
  FROM foods f
  JOIN food_nutrients fn ON f.food_id = fn.food_id
  JOIN nutrients n ON fn.nutrient_id = n.nutrient_id
  WHERE f.name = 'Apple juice'
  ORDER BY n.name;
  ```

- [ ] **Expected output**:
  ```
  Apple juice | Carbohydrate |  7.63
  Apple juice | Energy       | 30.00
  Apple juice | Fat          |  0.00
  Apple juice | Fiber        |  0.00
  Apple juice | Protein      |  0.00
  ```

#### 3. Test in App (5 minutes)
- [ ] **Open DiaTracker app** (http://localhost:5173)
- [ ] **Go to "Log Meal"**
- [ ] **Search for "Apple juice"**
- [ ] **Add 100g to meal**
- [ ] **Check prediction**:
  - Should use real values (0g protein, 0g fat, 0g fiber)
  - Predicted glucose should be realistic
- [ ] **Check "Today's Meals"** on homepage:
  - Should display meal with correct nutrients

#### 4. Test Different Foods (2 minutes)
- [ ] **Test high-protein food** (e.g., "Chicken nuggets"):
  - Should show ~15g protein (not 5.0g)
- [ ] **Test high-fat food** (e.g., "Vegetable oil"):
  - Should show ~93g fat (not 3.0g)
- [ ] **Test high-fiber food** (e.g., "Black beans"):
  - Should show ~39g fiber (not 2.0g)

---

## Verification Commands

### Quick Database Check
```sql
-- Check nutrient variety (should NOT all be 5.0, 3.0, 2.0)
SELECT 
  n.name as nutrient,
  MIN(fn.amount) as min_value,
  MAX(fn.amount) as max_value,
  AVG(fn.amount) as avg_value
FROM food_nutrients fn
JOIN nutrients n ON fn.nutrient_id = n.nutrient_id
GROUP BY n.name
ORDER BY n.name;
```

**Expected output** (variety, not all same):
```
 nutrient     | min_value | max_value | avg_value
--------------+-----------+-----------+-----------
 Carbohydrate |      0.00 |     83.64 |     35.21
 Energy       |      0.00 |    867.00 |    245.33
 Fat          |      0.00 |     93.33 |     12.45
 Fiber        |      0.00 |     39.50 |      5.67
 Protein      |      0.00 |     35.71 |      8.92
```

### Check Specific Foods
```sql
-- Apple juice (should be 0g protein, 0g fat, 0g fiber)
SELECT f.name, n.name, fn.amount 
FROM foods f
JOIN food_nutrients fn ON f.food_id = fn.food_id
JOIN nutrients n ON fn.nutrient_id = n.nutrient_id
WHERE f.name = 'Apple juice';

-- Chicken nuggets (should be ~15g protein)
SELECT f.name, n.name, fn.amount 
FROM foods f
JOIN food_nutrients fn ON f.food_id = fn.food_id
JOIN nutrients n ON fn.nutrient_id = n.nutrient_id
WHERE f.name = 'Chicken nuggets';

-- Black beans (should be ~39g fiber)
SELECT f.name, n.name, fn.amount 
FROM foods f
JOIN food_nutrients fn ON f.food_id = fn.food_id
JOIN nutrients n ON fn.nutrient_id = n.nutrient_id
WHERE f.name = 'Black beans';
```

---

## Troubleshooting

### Issue: "Enriched CSV not found"
**Solution**: Check file exists at `DiaTracker/datasets/gi_database_enriched.csv`

### Issue: "No module named 'sqlalchemy'"
**Solution**: Activate virtual environment:
```bash
cd DiaTracker/backend
venv\Scripts\activate
```

### Issue: Foods still show old values (5.0, 3.0, 2.0)
**Solution**: Database not reloaded yet. Follow Step 1 above.

### Issue: "Today's Meals" shows "No meals logged"
**Solution**: Already fixed in `foodApi.ts`. Just reload frontend:
```bash
# In frontend terminal
# Press Ctrl+C to stop
# Then restart: npm run dev
```

### Issue: Backend not starting
**Solution**: Check if port 8000 is already in use:
```bash
# Windows
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <PID> /F
```

---

## Success Criteria

### ✅ Database Reloaded Successfully
- Admin endpoint returns success message
- PostgreSQL shows 200 foods
- Nutrients show variety (not all 5.0, 3.0, 2.0)

### ✅ App Works Correctly
- Food search shows real nutritional data
- Meal predictions use accurate nutrients
- "Today's Meals" displays correctly
- Glucose predictions are realistic

### ✅ Ready for Thesis
- All data sources properly cited
- No hardcoded or estimated values
- Documentation complete
- Code production-ready

---

## After Completion

### Update Thesis
- [ ] Add USDA FoodData Central to bibliography
- [ ] Document cross-matching methodology (fuzzy matching, 100% success rate)
- [ ] Include enrichment statistics (138 high-confidence, 27 verified)
- [ ] Cite both Foster-Powell (GI/GL) and USDA (nutrients)

### Test Scenarios
- [ ] Log breakfast with multiple foods
- [ ] Check glucose prediction is realistic
- [ ] Verify daily summary shows correct totals
- [ ] Test meal history shows all logged meals

---

## Time Estimate

| Task | Time |
|------|------|
| Reload database | 5 min |
| Verify database | 3 min |
| Test in app | 5 min |
| Test different foods | 2 min |
| **TOTAL** | **15 min** |

---

## Reference Documents

- **Reload Instructions**: `RELOAD_DATABASE_INSTRUCTIONS.md`
- **Complete Summary**: `ENRICHMENT_COMPLETE_SUMMARY.md`
- **Enrichment Details**: `datasets/GI_DATABASE_ENRICHMENT_SUMMARY.md`
- **Model Formulas**: `datasets/MODEL_FORMULAS_AND_CALCULATIONS.md`

---

**Status**: Ready to Execute  
**Next Action**: Start with Step 1 (Reload Database)  
**Priority**: HIGH - Required for accurate predictions

---

## Quick Start (Copy-Paste)

```bash
# 1. Start backend
cd DiaTracker/backend
venv\Scripts\activate
python main.py

# 2. In another terminal, call admin endpoint
curl -X POST http://localhost:8000/api/v1/admin/load-gi-database

# 3. Verify in PostgreSQL
psql -U postgres -d ml_diabetes_tracker
SELECT COUNT(*) FROM foods;  -- Should be 200
\q

# 4. Test in app
# Open http://localhost:5173
# Search for "Apple juice"
# Verify shows 0g protein, 0g fat, 0g fiber
```

---

**Ready to go!** 🚀
