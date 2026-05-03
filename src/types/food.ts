/**
 * TypeScript types for food-related data structures
 */

export interface NutrientInfo {
  nutrient_id: string;
  name: string;
  amount: number;
  unit: string;
  per_unit: string;
}

export interface FoodSearchResult {
  food_id: string;
  name: string;
  category: string;
  food_type?: string;
  allergens?: string[];
  calories_per_serving?: number;
}

export interface FoodDetail {
  food_id: string;
  name: string;
  description?: string;
  category: string;
  food_type?: string;
  allergens?: string[];
  nutrients: NutrientInfo[];
  created_at: string;
}

export interface FoodSearchResponse {
  foods: FoodSearchResult[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface NutritionalTotals {
  calories: number;
  protein_g: number;
  carbohydrates_g: number;
  fat_g: number;
  fiber_g: number;
  vitamins: Record<string, number>;
  minerals: Record<string, number>;
}

export interface FoodEntry {
  entry_id: string;
  user_id: string;
  food_id: string;
  food_name: string;
  quantity: number;
  unit: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  consumed_at: string;
  created_at: string;
  nutritional_totals: NutritionalTotals;
}

export interface FoodEntryCreate {
  food_id: string;
  quantity: number;
  unit: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  consumed_at: string;
}

export interface FoodEntryUpdate {
  quantity?: number;
  unit?: string;
  meal_type?: 'breakfast' | 'lunch' | 'dinner' | 'snack';
}

export interface FoodEntryListResponse {
  entries: FoodEntry[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DailyNutritionalSummary {
  date: string;
  total_calories: number;
  total_protein_g: number;
  total_carbohydrates_g: number;
  total_fat_g: number;
  total_fiber_g: number;
  meal_breakdown: Record<string, NutritionalTotals>;
}
