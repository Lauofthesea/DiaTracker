"""
Mark verified foods in the enriched database.
Updates data_source to indicate manual verification.
"""

import csv
from pathlib import Path

# Verified food names from needs_review.csv
VERIFIED_FOODS = {
    "Bagel white",
    "Sourdough wheat",
    "Pita bread white",
    "Crackers saltine",
    "All-Bran cereal",
    "Crackers water",
    "Crackers graham",
    "Oatmeal rolled oats",
    "Oatmeal steel cut",
    "Pasta protein enriched",
    "Spaghetti white",
    "Plum",
    "Chickpeas boiled",
    "Lentils red",
    "Lentils green",
    "Corn sweet",
    "Peas green",
    "Coca-Cola",
    "Fanta orange",
    "Gatorade",
    "M&Ms peanut",
    "Popcorn plain",
    "Chocolate bar Mars",
    "Chocolate bar Snickers",
    "Ice cream premium",
    "Milk 2%",
    "Peppers bell"
}

def mark_verified():
    """Update enriched CSV to mark verified foods."""
    
    script_dir = Path(__file__).parent
    enriched_csv = script_dir.parent.parent / "datasets" / "gi_database_enriched.csv"
    output_csv = script_dir.parent.parent / "datasets" / "gi_database_enriched_verified.csv"
    
    # Read enriched CSV
    with open(enriched_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        foods = list(reader)
    
    # Update verified foods
    verified_count = 0
    for food in foods:
        food_name = food['food_name']
        if food_name in VERIFIED_FOODS:
            food['data_source'] = "USDA FoodData Central (Manually Verified)"
            verified_count += 1
    
    # Write updated CSV
    fieldnames = list(foods[0].keys())
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(foods)
    
    print(f"✓ Updated {verified_count} verified foods")
    print(f"✓ Saved to: {output_csv}")
    print(f"\nNext: Rename gi_database_enriched_verified.csv to gi_database_enriched.csv")

if __name__ == "__main__":
    mark_verified()
