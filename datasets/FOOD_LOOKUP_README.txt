FOOD LOOKUP DATABASE
For Food Recommendations and Search

Created: April 30, 2026
Purpose: Enable food name search and recommendations in the application


WHAT IS THIS FILE

food_lookup_database.csv contains 343,877 real foods with:
- Food names (e.g., "Apple", "White Rice", "Chicken Breast")
- Nutritional information (carbs, calories, fiber, protein, sugar, sodium)
- Diabetes risk classification (Low_Risk, Medium_Risk, High_Risk)
- USDA food category


HOW THIS WORKS WITH THE TRAINING DATA

TRAINING DATA (food_X_train.csv, etc.)
Used to train the AI model
Contains only numbers (scaled features)
Purpose: Teach the AI to recognize patterns

FOOD LOOKUP DATABASE (food_lookup_database.csv)
Used in the live application
Contains food names and original nutritional values
Purpose: Show actual food recommendations to users


FILE STRUCTURE

Columns in food_lookup_database.csv:

fdc_id - Unique food identifier from USDA
food_name - Name of the food (e.g., "Banana", "Whole Wheat Bread")
data_type - Type of food data (foundation, branded, etc.)
food_category - Category name (e.g., "Fruits", "Vegetables")
category_code - Numeric category code
carbs_total - Total carbohydrates in grams
calories - Energy content in kcal
fiber - Dietary fiber in grams
protein - Protein content in grams
fat_total - Total fat in grams
sugars_total - Total sugars in grams
sodium - Sodium content in mg
diabetes_risk - Classification (Low_Risk, Medium_Risk, High_Risk)


DIABETES RISK DISTRIBUTION

Total Foods: 343,877

Medium_Risk: 202,676 foods (58.9%)
High_Risk: 138,331 foods (40.2%)
Low_Risk: 2,870 foods (0.8%)


HOW TO USE IN YOUR APPLICATION

Example 1: Search for a food by name

import pandas as pd
food_db = pd.read_csv('food_lookup_database.csv')

Search for apple
results = food_db[food_db['food_name'].str.contains('apple', case=False)]
print(results[['food_name', 'calories', 'carbs_total', 'diabetes_risk']])


Example 2: Get nutritional info for a specific food

food = food_db[food_db['fdc_id'] == 123456].iloc[0]
print(f"Food: {food['food_name']}")
print(f"Calories: {food['calories']} kcal")
print(f"Carbs: {food['carbs_total']}g")
print(f"Risk: {food['diabetes_risk']}")


Example 3: Recommend safe foods for diabetic patients

Show only Low and Medium risk foods
safe_foods = food_db[food_db['diabetes_risk'].isin(['Low_Risk', 'Medium_Risk'])]
print(f"Safe food options: {len(safe_foods):,}")


Example 4: Filter by category

Get all fruits
fruits = food_db[food_db['food_category'].str.contains('fruit', case=False, na=False)]
print(fruits[['food_name', 'diabetes_risk']].head(20))


Example 5: Build a recommendation system

def recommend_foods(user_has_diabetes, search_term=""):
    if user_has_diabetes:
        Recommend Low and Medium risk foods only
        recommended = food_db[food_db['diabetes_risk'].isin(['Low_Risk', 'Medium_Risk'])]
    else:
        Show all foods
        recommended = food_db.copy()
    
    If user searched for something
    if search_term:
        recommended = recommended[recommended['food_name'].str.contains(search_term, case=False)]
    
    return recommended[['food_name', 'calories', 'carbs_total', 'diabetes_risk']].head(50)

Usage
results = recommend_foods(user_has_diabetes=True, search_term="chicken")
print(results)


TYPICAL USER FLOW

1. User logs in
2. System checks: Does user have diabetes? (using diabetes prediction model)
3. User searches for food: "chicken breast"
4. System queries food_lookup_database.csv
5. System filters results based on diabetes status
6. System shows:
   - Food name
   - Nutritional info
   - Diabetes risk level
   - Recommendation (Safe / Caution / Avoid)


INTEGRATION WITH ML MODELS

Model 1: Diabetes Prediction
Input: Patient medical data
Output: Has diabetes (Yes/No)
Use: Determine which foods to recommend

Model 2: Food Classification
Input: Food nutritional values
Output: Diabetes risk (Low/Medium/High)
Use: Already calculated in this database

Food Lookup Database
Input: User search query
Output: List of foods with names and nutrition
Use: Show actual recommendations to user


FILE SIZE AND PERFORMANCE

File size: 35.6 MB
Total foods: 343,877
Load time: approximately 2-3 seconds
Memory usage: approximately 50-100 MB

For better performance:
- Load once at application startup
- Keep in memory
- Use pandas for fast filtering
- Consider adding database indexing if using SQL


NOTES FOR PROGRAMMER

This database contains ORIGINAL nutritional values (not scaled)
The training data contains SCALED values (mean=0, std=1)
Do not mix them up

When user inputs a new food:
1. Get nutritional values
2. Scale them using food_scaler.pkl
3. Pass to trained model for prediction
4. Show result to user

When user searches existing foods:
1. Query this database
2. Filter by diabetes risk
3. Show results directly (no model needed)


ADDITIONAL FILES

food_lookup_usage_examples.txt - Sample foods and code examples
food_scaler.pkl - Scaler for converting new foods to model input
food_encoders.pkl - Encoders for categorical features
food_feature_names.txt - List of features used in model


SUMMARY

Training files: Train the AI model
Food lookup database: Show recommendations to users
Together they create: Complete diabetes support system

The programmer now has everything needed to build a working application.
