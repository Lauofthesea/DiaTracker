/**
 * Food and food entry API service functions
 */

import { apiClient, API_ENDPOINTS, handleApiError } from './api';
import type {
  FoodSearchResponse,
  FoodSearchResult,
  FoodDetail,
  FoodEntry,
  FoodEntryCreate,
  FoodEntryUpdate,
  FoodEntryListResponse,
  DailyNutritionalSummary,
} from '../types/food';

/**
 * Search foods with filters and pagination
 */
export const searchFoods = async (params: {
  q?: string;
  category?: string;
  allergens?: string[];
  page?: number;
  page_size?: number;
}): Promise<FoodSearchResponse> => {
  try {
    const queryParams = new URLSearchParams();
    
    if (params.q) queryParams.append('q', params.q);
    if (params.category) queryParams.append('category', params.category);
    if (params.allergens && params.allergens.length > 0) {
      queryParams.append('allergens', params.allergens.join(','));
    }
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.page_size) queryParams.append('page_size', params.page_size.toString());
    
    const response = await apiClient.get<FoodSearchResponse>(
      `${API_ENDPOINTS.FOODS.SEARCH}?${queryParams.toString()}`
    );
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Autocomplete food search (for quick search)
 */
export const autocompleteFoods = async (
  query: string,
  limit: number = 10
): Promise<FoodSearchResult[]> => {
  try {
    const response = await apiClient.get<FoodSearchResult[]>(
      `${API_ENDPOINTS.FOODS.AUTOCOMPLETE}?q=${encodeURIComponent(query)}&limit=${limit}`
    );
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Get all food categories
 */
export const getFoodCategories = async (): Promise<string[]> => {
  try {
    const response = await apiClient.get<string[]>(API_ENDPOINTS.FOODS.CATEGORIES);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Get detailed food information
 */
export const getFoodDetail = async (foodId: string): Promise<FoodDetail> => {
  try {
    const response = await apiClient.get<FoodDetail>(
      API_ENDPOINTS.FOODS.GET_BY_ID(foodId)
    );
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Create a new food entry
 */
export const createFoodEntry = async (
  data: FoodEntryCreate
): Promise<FoodEntry> => {
  try {
    const response = await apiClient.post<FoodEntry>(
      API_ENDPOINTS.FOOD_ENTRIES.CREATE,
      data
    );
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Get food entries with filters and pagination
 */
export const getFoodEntries = async (params: {
  start_date?: string;
  end_date?: string;
  meal_type?: string;
  page?: number;
  page_size?: number;
}): Promise<FoodEntryListResponse> => {
  try {
    const queryParams = new URLSearchParams();
    
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    if (params.meal_type) queryParams.append('meal_type', params.meal_type);
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.page_size) queryParams.append('page_size', params.page_size.toString());
    
    const response = await apiClient.get<FoodEntryListResponse>(
      `${API_ENDPOINTS.FOOD_ENTRIES.LIST}?${queryParams.toString()}`
    );
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Get daily nutritional summary
 */
export const getDailySummary = async (date: string): Promise<DailyNutritionalSummary> => {
  try {
    const response = await apiClient.get<DailyNutritionalSummary>(
      `${API_ENDPOINTS.FOOD_ENTRIES.DAILY_SUMMARY}?date=${date}`
    );
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Update a food entry
 */
export const updateFoodEntry = async (
  entryId: string,
  data: FoodEntryUpdate
): Promise<FoodEntry> => {
  try {
    const response = await apiClient.put<FoodEntry>(
      API_ENDPOINTS.FOOD_ENTRIES.UPDATE(entryId),
      data
    );
    return response.data;
  } catch (error) {
    // Check if it's a 403 error (edit window expired)
    if ((error as any).response?.status === 403) {
      throw new Error('Cannot edit entries older than 7 days');
    }
    throw new Error(handleApiError(error));
  }
};

/**
 * Delete a food entry
 */
export const deleteFoodEntry = async (entryId: string): Promise<void> => {
  try {
    await apiClient.delete(API_ENDPOINTS.FOOD_ENTRIES.DELETE(entryId));
  } catch (error) {
    // Check if it's a 403 error (edit window expired)
    if ((error as any).response?.status === 403) {
      throw new Error('Cannot delete entries older than 7 days');
    }
    throw new Error(handleApiError(error));
  }
};
