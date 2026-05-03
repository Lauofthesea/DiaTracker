export interface CurrentHealthMetrics {
  weight_kg: number;
  blood_sugar_mgdl: number;
  age: number;
  height_cm: number;
  bmi: number;
  recorded_at: string;
}

export interface ProfileResponse {
  user_id: string;
  name: string;
  email: string;
  age: number | null;
  height_cm: number | null;
  gender: string | null;
  is_pregnant: boolean | null;
  allergen_preferences: string[] | null;
  dietary_restrictions: string[] | null;
  health_conditions: string[] | null;
  current_health_metrics: CurrentHealthMetrics | null;
  created_at: string;
  last_login: string | null;
}

export interface ProfileUpdate {
  name?: string;
  age?: number;
  height_cm?: number;
  gender?: string;
  is_pregnant?: boolean;
  allergen_preferences?: string[];
  dietary_restrictions?: string[];
  health_conditions?: string[];
}

export interface HealthMetricsHistoryItem {
  metric_id: string;
  weight_kg: number;
  blood_sugar_mgdl: number;
  age: number;
  height_cm: number;
  bmi: number;
  symptoms: string[] | null;
  recorded_at: string;
  prediction: {
    prediction_id: string;
    classification: string;
    confidence: number;
  } | null;
}

export interface HealthMetricsHistoryResponse {
  metrics: HealthMetricsHistoryItem[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}
