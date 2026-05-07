"""
Match Foster-Powell GI database with local USDA food_lookup_database.csv

This script:
1. Reads gi_database_research_only.csv (200 foods with GI/GL)
2. Reads food_lookup_database.csv (343,877 foods with nutrients)
3. Matches foods by name using fuzzy matching
4. Creates enriched CSV with complete nutritional data
"""

import csv
import logging
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from difflib import SequenceMatcher, get_close_matches

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def similarity_ratio(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def normalize_food_name(name: str) -> str:
    """Normalize food name for better matching."""
    # Convert to lowercase
    name = name.lower().strip()
    
    # Remove common words that might differ
    remove_words = ['raw', 'cooked', 'fresh', 'frozen', 'canned', 'dried', 'organic']
    for word in remove_words:
        name = name.replace(f' {word}', '')
        name = name.replace(f'{word} ', '')
    
    # Remove extra spaces
    name = ' '.join(name.split())
    
    return name


def find_best_match(
    gi_food_name: str,
    usda_foods: List[Dict],
    threshold: float = 0.6
) -> Tuple[Optional[Dict], float]:
    """
    Find best matching USDA food for a GI database food.
    
    Args:
        gi_food_name: Name from GI database
        usda_foods: List of USDA food dictionaries
        threshold: Minimum similarity score (0-1)
        
    Returns:
        Tuple of (best_match_dict, similarity_score) or (None, 0.0)
    """
    gi_normalized = normalize_food_name(gi_food_name)
    
    best_match = None
    best_score = 0.0
    
    # First pass: exact match on normalized names
    for usda_food in usda_foods:
        usda_normalized = normalize_food_name(usda_food['food_name'])
        
        if gi_normalized == usda_normalized:
            return usda_food, 1.0
    
    # Second pass: fuzzy matching
    for usda_food in usda_foods:
        usda_name = usda_food['food_name']
        
        # Calculate similarity
        score = similarity_ratio(gi_food_name, usda_name)
        
        # Bonus for word matches
        gi_words = set(gi_normalized.split())
        usda_words = set(normalize_food_name(usda_name).split())
        word_overlap = len(gi_words & usda_words) / max(len(gi_words), 1)
        
        # Combined score
        combined_score = (score * 0.7) + (word_overlap * 0.3)
        
        if combined_score > best_score:
            best_score = combined_score
            best_match = usda_food
    
    if best_score >= threshold:
        return best_match, best_score
    
    return None, 0.0


def load_usda_database(csv_path: Path) -> List[Dict]:
    """Load USDA food lookup database."""
    logger.info(f"Loading USDA database from: {csv_path}")
    
    foods = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            foods.append(row)
    
    logger.info(f"Loaded {len(foods):,} foods from USDA database")
    return foods


def match_and_enrich():
    """Main function to match GI database with USDA database."""
    
    # Paths
    script_dir = Path(__file__).parent
    gi_csv_path = script_dir.parent.parent / "datasets" / "gi_database_research_only.csv"
    usda_csv_path = script_dir.parent.parent / "datasets" / "food_lookup_database.csv"
    output_csv_path = script_dir.parent.parent / "datasets" / "gi_database_enriched.csv"
    manual_review_path = script_dir.parent.parent / "datasets" / "gi_database_needs_review.csv"
    
    if not gi_csv_path.exists():
        logger.error(f"GI database not found at: {gi_csv_path}")
        return
    
    if not usda_csv_path.exists():
        logger.error(f"USDA database not found at: {usda_csv_path}")
        return
    
    # Load databases
    logger.info("=" * 80)
    logger.info("Loading databases...")
    logger.info("=" * 80)
    
    usda_foods = load_usda_database(usda_csv_path)
    
    with open(gi_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        gi_foods = list(reader)
    
    logger.info(f"Loaded {len(gi_foods)} foods from GI database")
    
    # Match foods
    logger.info("\n" + "=" * 80)
    logger.info("Matching foods...")
    logger.info("=" * 80 + "\n")
    
    enriched_foods = []
    needs_review = []
    
    matched_count = 0
    low_confidence_count = 0
    unmatched_count = 0
    
    for i, gi_food in enumerate(gi_foods):
        food_name = gi_food['food_name']
        category = gi_food['food_category']
        
        logger.info(f"[{i+1}/{len(gi_foods)}] {food_name}")
        
        # Skip reference foods
        if category == "Reference":
            logger.info(f"  → Skipping reference food")
            continue
        
        # Find best match
        best_match, score = find_best_match(food_name, usda_foods, threshold=0.5)
        
        if best_match:
            # Extract nutrients (values are per 100g in USDA database)
            enriched_food = {
                **gi_food,  # Keep all original GI data
                "usda_fdc_id": best_match['fdc_id'],
                "usda_food_name": best_match['food_name'],
                "match_score": round(score, 3),
                "calories_per_100g": float(best_match['calories']),
                "protein_per_100g": float(best_match['protein']),
                "fat_per_100g": float(best_match['fat_total']),
                "fiber_per_100g": float(best_match['fiber']),
                "carbohydrates_per_100g": float(best_match['carbs_total']),
                "data_source": "USDA FoodData Central (Local Match)"
            }
            
            enriched_foods.append(enriched_food)
            
            if score >= 0.8:
                logger.info(f"  ✓ HIGH confidence match ({score:.2f}): {best_match['food_name']}")
                logger.info(f"    Nutrients: {best_match['calories']} kcal, "
                          f"P:{best_match['protein']}g, F:{best_match['fat_total']}g, "
                          f"C:{best_match['carbs_total']}g, Fiber:{best_match['fiber']}g")
                matched_count += 1
            else:
                logger.info(f"  ⚠ LOW confidence match ({score:.2f}): {best_match['food_name']}")
                logger.info(f"    Nutrients: {best_match['calories']} kcal, "
                          f"P:{best_match['protein']}g, F:{best_match['fat_total']}g, "
                          f"C:{best_match['carbs_total']}g, Fiber:{best_match['fiber']}g")
                logger.info(f"    → NEEDS MANUAL REVIEW")
                needs_review.append(enriched_food)
                low_confidence_count += 1
        else:
            # No match found
            enriched_food = {
                **gi_food,
                "usda_fdc_id": "",
                "usda_food_name": "",
                "match_score": 0.0,
                "calories_per_100g": 0.0,
                "protein_per_100g": 0.0,
                "fat_per_100g": 0.0,
                "fiber_per_100g": 0.0,
                "carbohydrates_per_100g": 0.0,
                "data_source": "No match - NEEDS MANUAL ENTRY"
            }
            
            enriched_foods.append(enriched_food)
            needs_review.append(enriched_food)
            unmatched_count += 1
            
            logger.info(f"  ✗ NO MATCH FOUND")
            logger.info(f"    → NEEDS MANUAL RESEARCH")
    
    # Write enriched CSV
    if enriched_foods:
        fieldnames = list(enriched_foods[0].keys())
        
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched_foods)
        
        logger.info("\n" + "=" * 80)
        logger.info("RESULTS")
        logger.info("=" * 80)
        logger.info(f"✓ Enriched database saved to: {output_csv_path}")
        logger.info(f"\nStatistics:")
        logger.info(f"  Total foods processed: {len(enriched_foods)}")
        logger.info(f"  High confidence matches (≥0.8): {matched_count}")
        logger.info(f"  Low confidence matches (0.5-0.8): {low_confidence_count}")
        logger.info(f"  No matches (<0.5): {unmatched_count}")
        logger.info(f"  Needs manual review: {len(needs_review)}")
        
        # Write foods that need review
        if needs_review:
            with open(manual_review_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(needs_review)
            
            logger.info(f"\n⚠ Foods needing review saved to: {manual_review_path}")
            logger.info(f"  Please manually verify these {len(needs_review)} foods")
        
        logger.info("\n" + "=" * 80)
        logger.info("NEXT STEPS")
        logger.info("=" * 80)
        logger.info("1. Review gi_database_needs_review.csv")
        logger.info("2. Manually verify low-confidence matches")
        logger.info("3. Research and add data for unmatched foods")
        logger.info("4. Update gi_database_enriched.csv with corrections")
        logger.info("5. Update admin.py to use enriched CSV")
        logger.info("=" * 80)
    else:
        logger.error("No foods were enriched!")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("GI Database Enrichment with Local USDA Database")
    print("=" * 80)
    print("\nThis script will:")
    print("1. Read Foster-Powell GI database (200 foods)")
    print("2. Match with local USDA food_lookup_database.csv (343,877 foods)")
    print("3. Use fuzzy name matching to find best matches")
    print("4. Create enriched CSV with complete nutritional data")
    print("5. Flag low-confidence matches for manual review")
    print("=" * 80)
    
    input("\nPress Enter to continue...")
    
    match_and_enrich()
