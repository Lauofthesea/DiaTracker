/**
 * Meal Risk API client
 */

import { apiClient } from './api';

export interface MealPrediction {
  prediction_id: string;
  predicted_glucose_1hr: number;
  risk_level: 'Low' | 'Mid' | 'High';
  meal_composition: {
    available_carbs_g: number;
    fat_g: number;
    protein_g: number;
    fiber_g: number;
  };
  confidence_interval: {
    lower: number | null;
    upper: number | null;
  };
  predicted_at: string;
  food_entry_id: string | null;
}

export interface MealHistoryResponse {
  predictions: MealPrediction[];
  pagination: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
  };
}

/**
 * Get meal prediction history for a date range
 */
export const getMealHistory = async (
  startDate?: string,
  endDate?: string,
  riskLevel?: 'Low' | 'Mid' | 'High',
  page: number = 1,
  pageSize: number = 20
): Promise<MealHistoryResponse> => {
  const params = new URLSearchParams();
  
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  if (riskLevel) params.append('risk_level', riskLevel);
  params.append('page', page.toString());
  params.append('page_size', pageSize.toString());
  
  const response = await apiClient.get(`/meal-risk/history?${params.toString()}`);
  return response.data;
};

/**
 * Get today's meal predictions
 */
export const getTodaysMealPredictions = async (): Promise<MealPrediction[]> => {
  const today = new Date();
  const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const endOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 23, 59, 59);
  
  const startDate = startOfDay.toISOString();
  const endDate = endOfDay.toISOString();
  
  const response = await getMealHistory(startDate, endDate, undefined, 1, 100);
  return response.predictions;
};

/**
 * Predict glucose response for a meal
 */
export interface PredictMealRequest {
  available_carbs_g: number;
  fat_g: number;
  protein_g: number;
  fiber_g: number;
  fasting_glucose?: number;
  food_entry_id?: string;
}

export interface PredictMealResponse {
  prediction_id: string;
  predicted_glucose_1hr: number;
  confidence_interval: {
    lower: number;
    upper: number;
  };
  risk_level: 'Low' | 'Mid' | 'High';
  risk_explanation: string;
  model_version: string;
  predicted_at: string;
  warnings: string[];
}

export const predictMealRisk = async (request: PredictMealRequest): Promise<PredictMealResponse> => {
  const response = await apiClient.post('/meal-risk/predict', request);
  return response.data;
};
