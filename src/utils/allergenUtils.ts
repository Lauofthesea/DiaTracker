/**
 * Utility functions for allergen checking
 */

/**
 * Check if a food item contains any of the user's allergens
 * @param foodAllergens - Array of allergens in the food item
 * @param userAllergens - Array of user's allergen preferences
 * @returns true if food contains any user allergens, false otherwise
 */
export const foodMatchesAllergens = (
  foodAllergens: string[] | null | undefined,
  userAllergens: string[] | null | undefined
): boolean => {
  if (!foodAllergens || !userAllergens || foodAllergens.length === 0 || userAllergens.length === 0) {
    return false;
  }

  // Check if any food allergen matches any user allergen (case-insensitive)
  return foodAllergens.some((foodAllergen) =>
    userAllergens.some(
      (userAllergen) => foodAllergen.toLowerCase() === userAllergen.toLowerCase()
    )
  );
};

/**
 * Get list of matching allergens between food and user preferences
 * @param foodAllergens - Array of allergens in the food item
 * @param userAllergens - Array of user's allergen preferences
 * @returns Array of matching allergen names
 */
export const getMatchingAllergens = (
  foodAllergens: string[] | null | undefined,
  userAllergens: string[] | null | undefined
): string[] => {
  if (!foodAllergens || !userAllergens || foodAllergens.length === 0 || userAllergens.length === 0) {
    return [];
  }

  const matches: string[] = [];
  foodAllergens.forEach((foodAllergen) => {
    userAllergens.forEach((userAllergen) => {
      if (foodAllergen.toLowerCase() === userAllergen.toLowerCase()) {
        matches.push(foodAllergen);
      }
    });
  });

  return matches;
};
