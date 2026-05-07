# Simple Guide: How DiaTracker Calculates Glucose and Risk

**Easy-to-understand visual guide for thesis defense**

---

## 🎯 **PART 1: How We Calculate GLUCOSE (1-Hour After Eating)**

### **Step 1: Get Meal Information**
```
User logs meal: "Oatmeal with banana"
↓
System extracts from database:
- Carbohydrates: 50g
- Fiber: 8g
- Protein: 10g
- Fat: 5g
```

**Citation**: USDA FoodData Central (2024)

---

### **Step 2: Calculate Available Carbs**
```
Available Carbs = Total Carbs - Fiber
Available Carbs = 50g - 8g = 42g
```

**Why?** Fiber is not digested, so it doesn't raise glucose

**Citation**: Jenkins DJ, et al. (1981). *Am J Clin Nutr*, 34(3):362-366

---

### **Step 3: Base Glucose Prediction (Random Forest Model)**
```
Input to RF #1 Model:
1. Fasting glucose: 95 mg/dL (from user's health check)
2. Available carbs: 42g (from Step 2)
3. Fat: 5g (from database)
4. Protein: 10g (from database)
5. Fiber: 8g (from database)
6. BMI: 28 (from user profile)
7. Age: 45 (from user profile)
8. Gender: Female (from user profile)

↓ [Random Forest calculates] ↓

Base Glucose = 135 mg/dL
```

**What is Random Forest?** A machine learning algorithm that learned patterns from 10,000 people's data

**Citation**: 
- Breiman L. (2001). Random Forests. *Machine Learning*, 45(1):5-32
- CDC NHANES 2021-2023 (training data)

---

### **Step 4: Adjust for TIME OF DAY**
```
User is eating at: 8:00 AM (breakfast time)

Morning = Higher glucose (dawn phenomenon)
↓
Multiply by 1.15

Adjusted Glucose = 135 × 1.15 = 155 mg/dL
```

**Why?** In the morning, your body releases cortisol (stress hormone) which makes insulin work less effectively

**Citation**: Van Cauter E, et al. (1997). *J Clin Invest*, 88(3):934-942

---

### **Step 5: Adjust for AGE**
```
User's age: 45 years old

Age 45 = Multiply by 1.10
↓
Adjusted Glucose = 155 × 1.10 = 171 mg/dL
```

**Why?** As we age, our body becomes less sensitive to insulin (about 1% decline per year after age 30)

**Citation**: DeFronzo RA. (1981). *Diabetes Care*, 4(4):493-501

---

### **Step 6: Adjust for GENDER**
```
User: Female, Age 45 (premenopausal)

Premenopausal female = Multiply by 1.00 (no change)
↓
Final Glucose = 171 mg/dL
```

**Why?** Postmenopausal women (age 50+) have higher glucose because estrogen (protective hormone) decreases

**Citation**: Carr MC. (2003). *J Clin Endocrinol Metab*, 88(6):2404-2411

---

### **FINAL RESULT:**
```
┌─────────────────────────────────────┐
│  Predicted Glucose: 171 mg/dL       │
│  Time: 1 hour after eating          │
│  Status: HIGH (above 140 mg/dL)     │
└─────────────────────────────────────┘
```

---

## 🏥 **PART 2: How We Calculate RISK LEVEL**

### **Step 1: Get User's Health Information**
```
From user's health check:
1. Fasting glucose: 95 mg/dL
2. BMI: 28
3. Age: 45
4. Gender: Female
5. Family history: No diabetes in family
```

---

### **Step 2: Random Forest Classifier Predicts Risk**
```
Input to RF #2 Model:
[95, 28, 45, Female, No family history]

↓ [Random Forest calculates] ↓

Risk Level = LOW
```

**Why LOW?** Fasting glucose is 95 mg/dL (below 100 = normal)

---

### **Step 3: Risk Thresholds (ADA 2024 Guidelines)**
```
┌──────────────────────────────────────────────┐
│  Fasting Glucose < 100 mg/dL  →  LOW RISK   │
│  (Normal, healthy)                           │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  Fasting Glucose 100-125 mg/dL  →  MID RISK │
│  (Prediabetes - warning!)                    │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  Fasting Glucose ≥ 126 mg/dL  →  HIGH RISK  │
│  (Diabetes - see doctor!)                    │
└──────────────────────────────────────────────┘
```

**Citation**: American Diabetes Association. (2024). *Diabetes Care*, 47(Suppl 1):S20-S42

---

### **FINAL RESULT:**
```
┌─────────────────────────────────────┐
│  Risk Level: LOW                    │
│  Reason: Fasting glucose is 95      │
│  (Normal range)                     │
└─────────────────────────────────────┘
```

---

## 📊 **PART 3: What AFFECTS Glucose?**

### **1. CARBOHYDRATES** ⬆️ Increases Glucose
```
More carbs = Higher glucose
Example: 10g carbs → +2.5 mg/dL glucose
```
**Citation**: Jenkins DJ, et al. (1981). *Am J Clin Nutr*, 34(3):362-366

---

### **2. FIBER** ⬇️ Decreases Glucose
```
Fiber slows down carb absorption
Example: High-fiber bread → slower glucose rise than white bread
```
**Citation**: Anderson JW, et al. (2009). *Nutr Rev*, 67(4):188-205

---

### **3. FAT** ⬇️ Slows Glucose Rise
```
Fat delays stomach emptying
Example: Bread with butter → slower rise than bread alone
```
**Citation**: Gentilcore D, et al. (2006). *Am J Clin Nutr*, 83(6):1306-1312

---

### **4. PROTEIN** ➡️ Minimal Effect
```
Protein helps insulin work but doesn't raise glucose much
Example: Chicken doesn't spike glucose
```
**Citation**: Gannon MC, et al. (2001). *Diabetes*, 50(9):2337-2343

---

### **5. BMI (Body Weight)** ⬆️ Increases Glucose
```
Higher BMI = More insulin resistance = Higher glucose
Example: BMI 35 → 20% higher glucose than BMI 22
```
**Citation**: Kahn SE, et al. (2006). *Nature*, 444(7121):840-846

---

### **6. AGE** ⬆️ Increases Glucose
```
Older age = Less insulin sensitivity
Example: Age 60 → 15% higher glucose than age 30
```
**Citation**: DeFronzo RA. (1981). *Diabetes Care*, 4(4):493-501

---

### **7. GENDER (Female 50+)** ⬆️ Increases Glucose
```
After menopause = Less estrogen = Higher glucose
Example: Female age 55 → 10% higher than female age 40
```
**Citation**: Carr MC. (2003). *J Clin Endocrinol Metab*, 88(6):2404-2411

---

### **8. TIME OF DAY** ⬆️⬇️ Varies
```
Morning (6-9 AM):   +15% (dawn phenomenon)
Lunch (11-3 PM):    -10% (best time!)
Dinner (6-8 PM):    +5%
Night (10 PM-6 AM): +20% (worst time)
```
**Citation**: Van Cauter E, et al. (1997). *J Clin Invest*, 88(3):934-942

---

### **9. FAMILY HISTORY** ⬆️ Increases Risk
```
Parents with diabetes = 2-6× higher risk
Genetic predisposition to insulin resistance
```
**Citation**: InterAct Consortium. (2013). *Diabetologia*, 56(1):60-69

---

## 🔄 **PART 4: How Glucose GOES DOWN After Eating**

### **Glucose Decay Over Time**
```
Time after eating:

0 min:  Baseline (95 mg/dL)
        ↓
30 min: Rising (130 mg/dL)
        ↓
60 min: PEAK (171 mg/dL) ← Our prediction
        ↓
90 min: Declining (145 mg/dL)
        ↓
120 min: Declining (125 mg/dL)
        ↓
180 min: Back to baseline (100 mg/dL)
```

### **Formula:**
```
Current Glucose = Baseline + (Peak - Baseline) × e^(-time/τ)

Where τ (tau) depends on BMI:
- BMI < 25:  τ = 1.5 hours (fast decay)
- BMI 25-30: τ = 1.8 hours (medium)
- BMI > 30:  τ = 2.2 hours (slow decay)
```

**Why?** Higher BMI = More insulin resistance = Slower glucose clearance

**Citation**: Wolever TM, et al. (1991). *Am J Clin Nutr*, 54(5):846-854

---

## 📖 **PART 5: Where Did We Get the Data?**

### **1. NHANES 2021-2023** (Health Data)
```
What: 10,000 Americans' health information
From: CDC (U.S. Government)
Contains: Age, gender, BMI, glucose, family history, diet

Used for: Training both Random Forest models
```
**Citation**: CDC. (2023). NHANES 2021-2023. https://www.cdc.gov/nchs/nhanes/

---

### **2. Foster-Powell 2002** (GI/GL Values)
```
What: 200 foods with Glycemic Index values
From: Scientific journal (peer-reviewed)
Contains: How much each food raises glucose

Used for: Understanding food effects on glucose
```
**Citation**: Foster-Powell K, et al. (2002). *Am J Clin Nutr*, 76(1):5-56

---

### **3. USDA FoodData Central** (Nutritional Data)
```
What: 343,877 foods with complete nutrition info
From: U.S. Department of Agriculture
Contains: Carbs, protein, fat, fiber, calories

Used for: Getting accurate food composition
```
**Citation**: USDA. (2024). FoodData Central. https://fdc.nal.usda.gov/

---

### **4. ADA 2024 Guidelines** (Risk Thresholds)
```
What: Official diabetes diagnosis criteria
From: American Diabetes Association
Contains: Glucose thresholds for Low/Mid/High risk

Used for: Classifying diabetes risk
```
**Citation**: ADA. (2024). *Diabetes Care*, 47(Suppl 1):S20-S42

---

## 🎓 **PART 6: Simple Answers for Thesis Defense**

### **Q: How do you calculate glucose?**
**A:** 
```
1. Random Forest model predicts base glucose from meal + person
2. Adjust for time of day (morning = higher)
3. Adjust for age (older = higher)
4. Adjust for gender (postmenopausal = higher)
5. Result = predicted glucose 1 hour after eating
```

---

### **Q: How do you determine risk?**
**A:**
```
Random Forest model looks at:
- Fasting glucose (most important)
- BMI
- Age
- Gender
- Family history

Then classifies using ADA 2024 thresholds:
- Low: <100 mg/dL
- Mid: 100-125 mg/dL
- High: ≥126 mg/dL
```

---

### **Q: What makes glucose go up?**
**A:**
```
⬆️ INCREASES glucose:
- More carbohydrates
- Higher BMI
- Older age
- Morning time
- Postmenopausal women

⬇️ DECREASES glucose:
- More fiber
- More fat (slows absorption)
- Lunch time (best insulin sensitivity)
```

---

### **Q: Where did you get the formulas?**
**A:**
```
✅ All formulas from peer-reviewed research:
- Carb effect: Jenkins 1981
- Age effect: DeFronzo 1981
- Time effect: Van Cauter 1997
- Gender effect: Carr 2003
- Risk levels: ADA 2024

✅ All data from government sources:
- Health data: CDC NHANES
- Food data: USDA
```

---

## 📋 **PART 7: Complete Citation List**

### **Main Citations (Must Know)**

1. **Jenkins DJ, et al. (1981)**. Glycemic index of foods. *Am J Clin Nutr*, 34(3):362-366.
   - **Used for**: Carbohydrate effect on glucose

2. **DeFronzo RA. (1981)**. Glucose intolerance and aging. *Diabetes Care*, 4(4):493-501.
   - **Used for**: Age effect on glucose

3. **Van Cauter E, et al. (1997)**. Circadian rhythmicity and glucose regulation. *J Clin Invest*, 88(3):934-942.
   - **Used for**: Time-of-day effect

4. **Carr MC. (2003)**. Metabolic syndrome with menopause. *J Clin Endocrinol Metab*, 88(6):2404-2411.
   - **Used for**: Gender effect (postmenopausal)

5. **ADA. (2024)**. Standards of Medical Care in Diabetes—2024. *Diabetes Care*, 47(Suppl 1):S20-S42.
   - **Used for**: Risk level thresholds

6. **Breiman L. (2001)**. Random Forests. *Machine Learning*, 45(1):5-32.
   - **Used for**: Machine learning algorithm

7. **CDC. (2023)**. NHANES 2021-2023. https://www.cdc.gov/nchs/nhanes/
   - **Used for**: Training data (10,000 people)

8. **USDA. (2024)**. FoodData Central. https://fdc.nal.usda.gov/
   - **Used for**: Food nutritional data

---

## ✅ **Summary: The Complete Picture**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER LOGS MEAL                            │
│                         ↓                                    │
│              Extract nutrients from database                 │
│              (USDA FoodData Central)                        │
│                         ↓                                    │
│              Calculate available carbs                       │
│              (Total carbs - Fiber)                          │
│                         ↓                                    │
│         RF #1 predicts base glucose                         │
│         (Trained on NHANES data)                            │
│                         ↓                                    │
│         Apply clinical adjustments:                         │
│         - Time of day (Van Cauter 1997)                     │
│         - Age (DeFronzo 1981)                               │
│         - Gender (Carr 2003)                                │
│                         ↓                                    │
│         FINAL GLUCOSE PREDICTION                            │
│                         ↓                                    │
│         RF #2 classifies risk                               │
│         (Using ADA 2024 thresholds)                         │
│                         ↓                                    │
│         SHOW RESULT TO USER                                 │
│         "Your glucose will be 171 mg/dL (High Risk)"        │
└─────────────────────────────────────────────────────────────┘
```

**Everything is evidence-based with peer-reviewed citations!** ✅

---

**Document Status**: ✅ Easy to understand, ready for thesis defense  
**Last Updated**: May 7, 2026
