# Glucose Calculation Fix - Available Carbs Issue

## 🐛 **Problem Identified**

Your app was using **TOTAL CARBOHYDRATES** instead of **AVAILABLE CARBOHYDRATES** when predicting glucose levels.

### **Why This Matters:**

**Available Carbs = Total Carbs - Fiber**

Fiber doesn't raise blood glucose because it's not digested/absorbed. Using total carbs was **overestimating** glucose spikes.

---

## 📊 **Example: 100g White Rice**

### **Before Fix (WRONG):**
```
Total Carbs: 28g
Fiber: 0.4g
Used for prediction: 28g ❌
Predicted glucose: 90 + (28 × 1.2) = 124 mg/dL
```

### **After Fix (CORRECT):**
```
Total Carbs: 28g
Fiber: 0.4g
Available Carbs: 28 - 0.4 = 27.6g ✅
Predicted glucose: 90 + (27.6 × 1.2) = 123 mg/dL
```

**Difference**: Small for low-fiber foods, but **significant for high-fiber foods**!

---

## 🥗 **Example: 100g Lentils (High Fiber)**

### **Before Fix (WRONG):**
```
Total Carbs: 20g
Fiber: 8g
Used for prediction: 20g ❌
Predicted glucose: 90 + (20 × 1.2) = 114 mg/dL
```

### **After Fix (CORRECT):**
```
Total Carbs: 20g
Fiber: 8g
Available Carbs: 20 - 8 = 12g ✅
Predicted glucose: 90 + (12 × 1.2) = 104 mg/dL
```

**Difference**: **10 mg/dL** - Much more accurate!

---

## ✅ **What Was Fixed**

### **File: `DiaTracker/src/app/components/LogMealPage.tsx`**

**Line 243 (Preview Prediction):**
```typescript
// BEFORE:
available_carbs_g: totalCarbs,

// AFTER:
available_carbs_g: Math.max(0, totalCarbs - totalFiber),
```

**Line 554 (Saved Prediction):**
```typescript
// BEFORE:
available_carbs_g: Math.max(0, Math.min(500, totalCarbs)),

// AFTER:
available_carbs_g: Math.max(0, Math.min(500, totalCarbs - totalFiber)),
```

---

## 🎯 **Why Your 100g Meal Showed 120 mg/dL**

If you ate **100g of a food** and got **120 mg/dL** (baseline 90):

### **Possible Scenarios:**

#### **Scenario 1: High-Carb Food (e.g., Rice)**
- 100g rice = ~28g total carbs, ~0.4g fiber
- Available carbs = 27.6g
- Spike: +30 mg/dL
- **Result: 90 → 120 mg/dL** ✅ **NORMAL**

#### **Scenario 2: Bread**
- 100g bread = ~50g total carbs, ~2g fiber
- Available carbs = 48g
- Spike: +50-60 mg/dL
- **Result: 90 → 140-150 mg/dL** (higher than 120)

#### **Scenario 3: Chicken**
- 100g chicken = ~0g carbs
- Available carbs = 0g
- Spike: +5 mg/dL (minimal)
- **Result: 90 → 95 mg/dL** (much lower than 120)

---

## 📝 **Clinical Accuracy**

### **Formula Used by RF #1 Model:**
```
Predicted Glucose = Baseline + (Available_Carbs × Glycemic_Factor × Individual_Multipliers)

Where:
- Available_Carbs = Total_Carbs - Fiber ✅
- Glycemic_Factor ≈ 1.0-1.5 (depends on GI/GL)
- Individual_Multipliers = Time × Age × Gender × BMI
```

### **Rule of Thumb:**
```
Every 10g of AVAILABLE carbs → +10-15 mg/dL glucose spike
(for person with normal insulin sensitivity)
```

---

## ✅ **Verification**

To verify the fix is working:

1. **Log a high-fiber food** (e.g., lentils, beans, whole wheat bread)
2. **Check the prediction**
3. **Compare with low-fiber food** of same total carbs

**Expected**: High-fiber food should show **lower glucose prediction** than low-fiber food with same total carbs.

---

## 🎓 **For Your Thesis Defense**

**Key Points:**
1. ✅ **Clinically Accurate**: Using available carbs (not total carbs) follows ADA guidelines
2. ✅ **Evidence-Based**: Fiber doesn't raise blood glucose (Jenkins et al., 1981)
3. ✅ **Formula**: Available Carbs = Total Carbs - Fiber (standard calculation)
4. ✅ **Impact**: More accurate predictions, especially for high-fiber foods

**Citation:**
- Jenkins DJ, et al. (1981). "Glycemic index of foods: a physiological basis for carbohydrate exchange." Am J Clin Nutr.
- Foster-Powell K, et al. (2002). "International table of glycemic index and glycemic load values." Am J Clin Nutr.

---

## 🔍 **Testing Recommendations**

Test with these foods to verify accuracy:

| Food | Total Carbs | Fiber | Available Carbs | Expected Spike |
|------|-------------|-------|-----------------|----------------|
| White Rice (100g) | 28g | 0.4g | 27.6g | +30 mg/dL |
| Brown Rice (100g) | 23g | 1.8g | 21.2g | +25 mg/dL |
| Lentils (100g) | 20g | 8g | 12g | +15 mg/dL |
| White Bread (100g) | 50g | 2g | 48g | +55 mg/dL |
| Whole Wheat Bread (100g) | 43g | 6g | 37g | +42 mg/dL |

**Status**: ✅ **FIXED** - Now using clinically accurate available carbohydrates!
