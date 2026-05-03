/**
 * Tests for food API functions
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from '../api';
import {
  searchFoods,
  autocompleteFoods,
  getFoodCategories,
  createFoodEntry,
  getFoodEntries,
  getDailySummary,
  updateFoodEntry,
  deleteFoodEntry,
} from '../foodApi';

// Mock the apiClient
vi.mock('../api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  API_ENDPOINTS: {
    FOODS: {
      SEARCH: '/foods/search',
      AUTOCOMPLETE: '/foods/autocomplete',
      CATEGORIES: '/foods/categories',
      GET_BY_ID: (id: string) => `/foods/${id}`,
    },
    FOOD_ENTRIES: {
      CREATE: '/food-entries',
      LIST: '/food-entries',
      DAILY_SUMMARY: '/food-entries/daily-summary',
      UPDATE: (id: string) => `/food-entries/${id}`,
      DELETE: (id: string) => `/food-entries/${id}`,
    },
  },
  handleApiError: (error: any) => error.message || 'Unknown error',
}));

describe('Food API Functions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('searchFoods', () => {
    it('should search foods with query parameters', async () => {
      const mockResponse = {
        data: {
          foods: [
            {
              food_id: '123',
              name: 'Apple',
              category: 'Fruits',
              calories_per_serving: 95,
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
          total_pages: 1,
        },
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await searchFoods({ q: 'apple', page: 1, page_size: 20 });

      expect(result).toEqual(mockResponse.data);
      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('/foods/search')
      );
    });

    it('should handle allergen filters', async () => {
      const mockResponse = {
        data: {
          foods: [],
          total: 0,
          page: 1,
          page_size: 20,
          total_pages: 0,
        },
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      await searchFoods({ allergens: ['Dairy', 'Nuts'] });

      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('allergens=Dairy%2CNuts')
      );
    });
  });

  describe('createFoodEntry', () => {
    it('should create a food entry', async () => {
      const mockEntry = {
        food_id: '123',
        quantity: 100,
        unit: 'g',
        meal_type: 'lunch' as const,
        consumed_at: '2024-01-15T12:00:00Z',
      };

      const mockResponse = {
        data: {
          entry_id: '456',
          ...mockEntry,
          food_name: 'Apple',
          user_id: '789',
          created_at: '2024-01-15T12:00:00Z',
          nutritional_totals: {
            calories: 95,
            protein_g: 0.5,
            carbohydrates_g: 25,
            fat_g: 0.3,
            fiber_g: 4,
            vitamins: {},
            minerals: {},
          },
        },
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const result = await createFoodEntry(mockEntry);

      expect(result).toEqual(mockResponse.data);
      expect(apiClient.post).toHaveBeenCalledWith('/food-entries', mockEntry);
    });
  });

  describe('getFoodEntries', () => {
    it('should get food entries with filters', async () => {
      const mockResponse = {
        data: {
          entries: [],
          total: 0,
          page: 1,
          page_size: 20,
          total_pages: 0,
        },
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await getFoodEntries({
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        meal_type: 'breakfast',
      });

      expect(result).toEqual(mockResponse.data);
      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('start_date=2024-01-01')
      );
    });
  });

  describe('deleteFoodEntry', () => {
    it('should delete a food entry', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: null });

      await deleteFoodEntry('123');

      expect(apiClient.delete).toHaveBeenCalledWith('/food-entries/123');
    });

    it('should throw error for entries older than 7 days', async () => {
      const error = {
        response: {
          status: 403,
          data: { error: { message: 'Cannot delete entries older than 7 days' } },
        },
      };

      vi.mocked(apiClient.delete).mockRejectedValue(error);

      await expect(deleteFoodEntry('123')).rejects.toThrow(
        'Cannot delete entries older than 7 days'
      );
    });
  });

  describe('updateFoodEntry', () => {
    it('should update a food entry', async () => {
      const updateData = {
        quantity: 150,
        unit: 'g',
      };

      const mockResponse = {
        data: {
          entry_id: '123',
          food_id: '456',
          food_name: 'Apple',
          user_id: '789',
          quantity: 150,
          unit: 'g',
          meal_type: 'lunch' as const,
          consumed_at: '2024-01-15T12:00:00Z',
          created_at: '2024-01-15T12:00:00Z',
          nutritional_totals: {
            calories: 142.5,
            protein_g: 0.75,
            carbohydrates_g: 37.5,
            fat_g: 0.45,
            fiber_g: 6,
            vitamins: {},
            minerals: {},
          },
        },
      };

      vi.mocked(apiClient.put).mockResolvedValue(mockResponse);

      const result = await updateFoodEntry('123', updateData);

      expect(result).toEqual(mockResponse.data);
      expect(apiClient.put).toHaveBeenCalledWith('/food-entries/123', updateData);
    });

    it('should throw error for entries older than 7 days', async () => {
      const error = {
        response: {
          status: 403,
          data: { error: { message: 'Cannot edit entries older than 7 days' } },
        },
      };

      vi.mocked(apiClient.put).mockRejectedValue(error);

      await expect(updateFoodEntry('123', { quantity: 150 })).rejects.toThrow(
        'Cannot edit entries older than 7 days'
      );
    });
  });

  describe('getDailySummary', () => {
    it('should get daily nutritional summary', async () => {
      const mockResponse = {
        data: {
          date: '2024-01-15',
          total_calories: 1850,
          total_protein_g: 95,
          total_carbohydrates_g: 210,
          total_fat_g: 62,
          total_fiber_g: 28,
          meal_breakdown: {
            breakfast: {
              calories: 450,
              protein_g: 20,
              carbohydrates_g: 60,
              fat_g: 15,
              fiber_g: 8,
              vitamins: {},
              minerals: {},
            },
          },
        },
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await getDailySummary('2024-01-15');

      expect(result).toEqual(mockResponse.data);
      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('date=2024-01-15')
      );
    });
  });

  describe('autocompleteFoods', () => {
    it('should autocomplete food search', async () => {
      const mockResponse = {
        data: [
          {
            food_id: '123',
            name: 'Apple',
            category: 'Fruits',
            calories_per_serving: 95,
          },
        ],
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await autocompleteFoods('app', 10);

      expect(result).toEqual(mockResponse.data);
      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('/foods/autocomplete')
      );
    });
  });

  describe('getFoodCategories', () => {
    it('should get all food categories', async () => {
      const mockResponse = {
        data: ['Fruits', 'Vegetables', 'Grains', 'Proteins'],
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await getFoodCategories();

      expect(result).toEqual(mockResponse.data);
      expect(apiClient.get).toHaveBeenCalledWith('/foods/categories');
    });
  });
});
