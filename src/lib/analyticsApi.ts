/**
 * Analytics API client functions
 */

import { apiClient, API_ENDPOINTS, handleApiError } from './api';

// Type definitions for analytics API responses
export interface MacronutrientDistribution {
  protein_percent: number;
  carbohydrates_percent: number;
  fat_percent: number;
}

export interface CarbohydrateWarning {
  date: string;
  carbohydrates_g: number;
  recommended_max_g: number;
  severity: 'moderate' | 'high';
  message: string;
}

export interface PeriodSummary {
  period: 'daily' | 'weekly' | 'monthly';
  start_date: string;
  end_date: string;
  total_calories: number;
  avg_daily_calories: number;
  total_protein_g: number;
  total_carbohydrates_g: number;
  total_fat_g: number;
  total_fiber_g: number;
  macronutrient_distribution: MacronutrientDistribution;
  warnings: CarbohydrateWarning[];
  days_with_data: number;
}

export interface DailyTrendData {
  date: string;
  calories: number;
  protein_g: number;
  carbohydrates_g: number;
  fat_g: number;
  fiber_g: number;
}

export interface NutritionalTrends {
  start_date: string;
  end_date: string;
  daily_data: DailyTrendData[];
  avg_calories: number;
  avg_protein_g: number;
  avg_carbohydrates_g: number;
  avg_fat_g: number;
}

/**
 * Fetch period summary (daily, weekly, or monthly)
 */
export const fetchPeriodSummary = async (
  period: 'daily' | 'weekly' | 'monthly',
  date: string
): Promise<PeriodSummary> => {
  try {
    const response = await apiClient.get<PeriodSummary>(
      API_ENDPOINTS.ANALYTICS.SUMMARY,
      {
        params: { period, date },
      }
    );
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Fetch nutritional trends over a date range
 */
export const fetchNutritionalTrends = async (
  startDate: string,
  endDate: string
): Promise<NutritionalTrends> => {
  try {
    const response = await apiClient.get<NutritionalTrends>(
      API_ENDPOINTS.ANALYTICS.TRENDS,
      {
        params: { start_date: startDate, end_date: endDate },
      }
    );
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Fetch average calories over a date range
 */
export const fetchAverageCalories = async (
  startDate: string,
  endDate: string
): Promise<number> => {
  try {
    const response = await apiClient.get<number>(
      '/analytics/average-calories',
      {
        params: { start_date: startDate, end_date: endDate },
      }
    );
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Fetch macronutrient distribution over a date range
 */
export const fetchMacronutrientDistribution = async (
  startDate: string,
  endDate: string
): Promise<MacronutrientDistribution> => {
  try {
    const response = await apiClient.get<MacronutrientDistribution>(
      '/analytics/macronutrient-distribution',
      {
        params: { start_date: startDate, end_date: endDate },
      }
    );
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Check for carbohydrate warning on a specific date
 */
export const fetchCarbohydrateWarning = async (
  date: string
): Promise<CarbohydrateWarning | null> => {
  try {
    const response = await apiClient.get<CarbohydrateWarning | null>(
      '/analytics/carbohydrate-warning',
      {
        params: { date },
      }
    );
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};
