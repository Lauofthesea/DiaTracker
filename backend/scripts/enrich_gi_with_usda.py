"""
Enrich Foster-Powell GI database with USDA nutritional data.

This script:
1. Reads gi_database_research_only.csv
2. For each food, searches USDA FoodData Central API
3. Retrieves accurate protein, fat, fiber, and calorie values
4. Creates enriched CSV with complete nutritional data
"""

import csv
import json
import time
import logging
from pathlib import Path
from typing import Dict, Optional, List
import requests
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# USDA FoodData Central API
# Get free API key from: https://fdc.nal.usda.gov/api-key-signup.html
USDA_API_KEY = "DEMO_KEY"  # Replace with your API key (DEMO_KEY has rate limits)
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
USDA_FOOD_URL = "https://api.nal.usda.gov/fdc/v1/food"


def similarity_ratio(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def search_usda_food(food_name: str, category: str = None) -> Optional[Dict]:
    """
    Search USDA FoodData Central for a food by name.
    
    Args:
        food_name: Name of the food to search
        category: Optional category to narrow search
        
    Returns:
        Best matching food data or None
    """
    try:
        # Clean food name for better matching
        search_term = food_name.lower().strip()
        
        # Add category context if available
        if category:
            search_term = f"{search_term} {category.lower()}"
        
        params = {
            "api_key": USDA_API_KEY,
            "query": search_term,
            "dataType": ["Survey (FNDDS)", "Foundation", "SR Legacy"],  # Prefer comprehensive databases
            "pageSize": 10,
            "pageNumber": 1,
            "sortBy": "dataType.keyword",
            "sortOrder": "asc"
        }
        
        response = requests.get(USDA_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        foods = data.get("foods", [])
        
        if not foods:
            logger.warning(f"No USDA match found for: {food_name}")
            return None
        
        # Find best match by name similarity
        best_match = None
        best_score = 0.0
        
        for food in foods:
            food_description = food.get("description", "")
            score = similarity_ratio(food_name, food_description)
            
            if score > best_score:
                best_score = score
                best_match = food
        
        if best_score < 0.5:  # Threshold for acceptable match
            logger.warning(f"Low confidence match for '{food_name}': {best_match.get('description')} (score: {best_score:.2f})")
        else:
            logger.info(f"Matched '{food_name}' -> '{best_match.get('description')}' (score: {best_score:.2f})")
        
        return best_match
        
    except requests.RequestException as e:
        logger.error(f"Error searching USDA for '{food_name}': {e}")
        return None


def extract_nutrients(food_data: Dict) -> Dict[str, float]:
    """
    Extract key nutrients from USDA food data.
    
    Returns:
        Dict with calories, protein, fat, fiber, carbs
    """
    nutrients = {
        "calories": 0.0,
        "protein_g": 0.0,
        "fat_g": 0.0,
        "fiber_g": 0.0,
        "carbohydrates_g": 0.0
    }
    
    food_nutrients = food_data.get("foodNutrients", [])
    
    for nutrient in food_nutrients:
        nutrient_name = nutrient.get("nutrientName", "").lower()
        nutrient_number = nutrient.get("nutrientNumber", "")
        value = nutrient.get("value", 0.0)
        
        # Energy (calories)
        if nutrient_number == "208" or "energy" in nutrient_name:
            unit = nutrient.get("unitName", "").lower()
            if "kcal" in unit:
                nutrients["calories"] = value
        
        # Protein
        elif nutrient_number == "203" or "protein" in nutrient_name:
            nutrients["protein_g"] = value
        
        # Total fat
        elif nutrient_number == "204" or ("fat" in nutrient_name and "fatty" not in nutrient_name):
            nutrients["fat_g"] = value
        
        # Fiber
        elif nutrient_number == "291" or "fiber" in nutrient_name:
            nutrients["fiber_g"] = value
        
        # Carbohydrates
        elif nutrient_number == "205" or "carbohydrate" in nutrient_name:
            nutrients["carbohydrates_g"] = value
    
    return nutrients


def enrich_gi_database():
    """Main function to enrich GI database with USDA data."""
    
    # Paths
    script_dir = Path(__file__).parent
    gi_csv_path = script_dir.parent.parent / "datasets" / "gi_database_research_only.csv"
    output_csv_path = script_dir.parent.parent / "datasets" / "gi_database_enriched.csv"
    
    if not gi_csv_path.exists():
        logger.error(f"GI database not found at: {gi_csv_path}")
        return
    
    # Read GI database
    with open(gi_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        gi_foods = list(reader)
    
    logger.info(f"Loaded {len(gi_foods)} foods from GI database")
    
    # Enrich with USDA data
    enriched_foods = []
    matched_count = 0
    unmatched_count = 0
    
    for i, gi_food in enumerate(gi_foods):
        food_name = gi_food['food_name']
        category = gi_food['food_category']
        
        logger.info(f"\n[{i+1}/{len(gi_foods)}] Processing: {food_name}")
        
        # Skip reference foods
        if category == "Reference":
            logger.info(f"Skipping reference food: {food_name}")
            continue
        
        # Search USDA
        usda_food = search_usda_food(food_name, category)
        
        if usda_food:
            # Extract nutrients
            nutrients = extract_nutrients(usda_food)
            
            # Create enriched record
            enriched_food = {
                **gi_food,  # Keep all original GI data
                "usda_fdc_id": usda_food.get("fdcId", ""),
                "usda_description": usda_food.get("description", ""),
                "calories_per_100g": round(nutrients["calories"], 2),
                "protein_per_100g": round(nutrients["protein_g"], 2),
                "fat_per_100g": round(nutrients["fat_g"], 2),
                "fiber_per_100g": round(nutrients["fiber_g"], 2),
                "carbohydrates_per_100g": round(nutrients["carbohydrates_g"], 2),
                "data_source": "USDA FoodData Central"
            }
            
            enriched_foods.append(enriched_food)
            matched_count += 1
            
            logger.info(f"✓ Enriched: {food_name}")
            logger.info(f"  Calories: {nutrients['calories']:.1f} kcal/100g")
            logger.info(f"  Protein: {nutrients['protein_g']:.1f}g, Fat: {nutrients['fat_g']:.1f}g, Fiber: {nutrients['fiber_g']:.1f}g")
        else:
            # No match found - use original GI data with estimated values
            enriched_food = {
                **gi_food,
                "usda_fdc_id": "",
                "usda_description": "",
                "calories_per_100g": 0.0,
                "protein_per_100g": 0.0,
                "fat_per_100g": 0.0,
                "fiber_per_100g": 0.0,
                "carbohydrates_per_100g": 0.0,
                "data_source": "No USDA match - needs manual entry"
            }
            
            enriched_foods.append(enriched_food)
            unmatched_count += 1
            
            logger.warning(f"✗ No match: {food_name}")
        
        # Rate limiting (DEMO_KEY allows 30 requests per hour)
        if USDA_API_KEY == "DEMO_KEY":
            time.sleep(2)  # 2 seconds between requests
    
    # Write enriched CSV
    if enriched_foods:
        fieldnames = list(enriched_foods[0].keys())
        
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched_foods)
        
        logger.info(f"\n✓ Enriched database saved to: {output_csv_path}")
        logger.info(f"  Total foods: {len(enriched_foods)}")
        logger.info(f"  Matched with USDA: {matched_count}")
        logger.info(f"  Unmatched: {unmatched_count}")
        logger.info(f"\nNext steps:")
        logger.info(f"1. Review {output_csv_path} for unmatched foods")
        logger.info(f"2. Manually add nutritional data for unmatched foods")
        logger.info(f"3. Update admin.py to use enriched CSV")
    else:
        logger.error("No foods were enriched!")


if __name__ == "__main__":
    print("=" * 80)
    print("GI Database Enrichment with USDA Nutritional Data")
    print("=" * 80)
    print("\nThis script will:")
    print("1. Read Foster-Powell GI database")
    print("2. Search USDA FoodData Central for each food")
    print("3. Extract accurate nutritional values")
    print("4. Create enriched CSV with complete data")
    print("\nNote: Using DEMO_KEY has rate limits (30 requests/hour)")
    print("Get a free API key at: https://fdc.nal.usda.gov/api-key-signup.html")
    print("=" * 80)
    
    input("\nPress Enter to continue...")
    
    enrich_gi_database()
