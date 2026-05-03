/**
 * Health Check service utilities
 */

import { apiClient, API_ENDPOINTS } from './api';
import { HealthMetrics, Prediction } from './types';

export interface HealthCheckSubmitRequest {
  weight: number;
  weight_unit: 'kg' | 'lbs';
  blood_sugar: number;
  age: number;
  height: number;
  height_unit: 'cm' | 'in';
  symptoms: string[];
}

export interface HealthCheckSubmitResponse {
  prediction_id: string;
  user_id: string;
  metric_id: string;
  model_version: string;
  classification: 'Type 1' | 'Type 2' | 'No Diabetes';
  confidence: number;
  probabilities: Record<string, number>;
  predicted_at: string;
}

/**
 * Submit health check data and get diabetes prediction
 */
export const submitHealthCheck = async (
  data: HealthCheckSubmitRequest
): Promise<HealthCheckSubmitResponse> => {
  // Convert units to what backend expects
  const weightKg = data.weight_unit === 'lbs' ? data.weight * 0.453592 : data.weight;
  const heightCm = data.height_unit === 'in' ? data.height * 2.54 : data.height;
  
  // Transform to backend format
  const backendData = {
    weight_kg: weightKg,
    blood_sugar_mgdl: data.blood_sugar,
    age: data.age,
    height_cm: heightCm,
    symptoms: data.symptoms,
  };
  
  const response = await apiClient.post<HealthCheckSubmitResponse>(
    API_ENDPOINTS.HEALTH_CHECK.SUBMIT,
    backendData
  );
  return response.data;
};

/**
 * Get health check history
 */
export const getHealthCheckHistory = async (): Promise<Prediction[]> => {
  const response = await apiClient.get<Prediction[]>(
    API_ENDPOINTS.HEALTH_CHECK.HISTORY
  );
  return response.data;
};

/**
 * Get latest health check prediction
 */
export const getLatestHealthCheck = async (): Promise<Prediction | null> => {
  try {
    const response = await apiClient.get<Prediction>(API_ENDPOINTS.HEALTH_CHECK.LATEST);
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 404) {
      return null;
    }
    throw error;
  }
};

/**
 * Validate health metrics ranges
 */
export const validateHealthMetrics = (data: HealthCheckSubmitRequest): { valid: boolean; errors: string[] } => {
  const errors: string[] = [];

  // Convert to kg for validation
  const weightKg = data.weight_unit === 'lbs' ? data.weight * 0.453592 : data.weight;
  if (weightKg < 20 || weightKg > 300) {
    errors.push('Weight must be between 20-300 kg (44-661 lbs)');
  }

  // Validate blood sugar
  if (data.blood_sugar < 20 || data.blood_sugar > 600) {
    errors.push('Blood sugar must be between 20-600 mg/dL');
  }

  // Validate age
  if (data.age < 1 || data.age > 120) {
    errors.push('Age must be between 1-120 years');
  }

  // Convert to cm for validation
  const heightCm = data.height_unit === 'in' ? data.height * 2.54 : data.height;
  if (heightCm < 50 || heightCm > 250) {
    errors.push('Height must be between 50-250 cm (20-98 inches)');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
};

/**
 * Calculate BMI from weight and height
 */
export const calculateBMI = (weight: number, weightUnit: 'kg' | 'lbs', height: number, heightUnit: 'cm' | 'in'): number => {
  // Convert to kg and cm
  const weightKg = weightUnit === 'lbs' ? weight * 0.453592 : weight;
  const heightCm = heightUnit === 'in' ? height * 2.54 : height;
  
  // Calculate BMI: weight (kg) / (height (m))^2
  const heightM = heightCm / 100;
  return weightKg / (heightM * heightM);
};

/**
 * Get BMI category
 */
export const getBMICategory = (bmi: number): string => {
  if (bmi < 18.5) return 'Underweight';
  if (bmi < 25) return 'Normal weight';
  if (bmi < 30) return 'Overweight';
  return 'Obese';
};
