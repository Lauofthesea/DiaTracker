/**
 * Type definitions for the ML Diabetes Tracker application
 */

// User types
export interface User {
  user_id: string;
  email: string;
  name: string;
  created_at: string;
  last_login?: string;
  first_login_completed: boolean;
}

// Health metrics types
export interface HealthMetrics {
  metric_id?: string;
  weight_kg: number;
  blood_sugar_mgdl: number;
  age: number;
  height_cm: number;
  bmi?: number;
  symptoms: Record<string, boolean>;
  recorded_at?: string;
}

// Prediction types
export interface Prediction {
  prediction_id: string;
  classification: 'Type 1' | 'Type 2' | 'No Diabetes';
  confidence: number;
  probabilities: Record<string, number>;
  predicted_at: string;
  metrics?: HealthMetrics;
}

// Food types
export interface Food {
  food_id: string;
  name: string;
  description?: string;
  category: string;
  food_type?: string;
  allergens: string[];
  nutritional_data?: NutritionalData;
  serving_sizes?: ServingSize[];
}

export interface NutritionalData {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber?: number;
  vitamins?: Record<string, number>;
  minerals?: Record<string, number>;
}

export interface ServingSize {
  unit: string;
  amount: number;
  description: string;
}

// Food entry types
export interface FoodEntry {
  entry_id: string;
  food: Food;
  quantity: number;
  unit: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  consumed_at: string;
  created_at: string;
  nutritional_totals: NutritionalData;
}

// User profile types
export interface UserProfile {
  user_id: string;
  allergen_preferences: string[];
  dietary_restrictions: string[];
  health_conditions: string[];
  updated_at: string;
}

// Analytics types
export interface NutritionalSummary {
  period: 'daily' | 'weekly' | 'monthly';
  start_date: string;
  end_date: string;
  total_calories: number;
  avg_daily_calories: number;
  macronutrients: {
    protein: number;
    carbs: number;
    fat: number;
  };
  micronutrients: Record<string, number>;
  warnings: string[];
}

export interface TrendData {
  daily_data: Array<{
    date: string;
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  }>;
}

// Authentication types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  user_id: string;
  token: string;
  expires_in: number;
  is_first_login?: boolean;
}

// Form types
export interface HealthCheckFormData {
  weight: number;
  weight_unit: 'kg' | 'lbs';
  blood_sugar: number;
  age: number;
  height: number;
  height_unit: 'cm' | 'in';
  symptoms: string[];
}

export interface FoodSearchFilters {
  query?: string;
  category?: string;
  allergens?: string[];
}

// API response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// Error types
export interface ApiError {
  code: string;
  message: string;
  details?: string;
  timestamp: string;
  request_id: string;
}