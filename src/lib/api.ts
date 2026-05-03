/**
 * API client configuration and utilities
 */

import axios from 'axios';

// API base URL - will be configurable via environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default configuration
export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      // Redirect to login page
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/auth/login',
    SIGNUP: '/auth/signup',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
  },
  
  // Health Check
  HEALTH_CHECK: {
    SUBMIT: '/health-check/submit',
    HISTORY: '/health-check/history',
    LATEST: '/health-check/latest',
  },
  
  // Foods
  FOODS: {
    SEARCH: '/foods/search',
    AUTOCOMPLETE: '/foods/autocomplete',
    CATEGORIES: '/foods/categories',
    GET_BY_ID: (id: string) => `/foods/${id}`,
    CREATE_CUSTOM: '/foods/custom',
  },
  
  // Food Entries
  FOOD_ENTRIES: {
    CREATE: '/food-entries',
    LIST: '/food-entries',
    DAILY_SUMMARY: '/food-entries/daily-summary',
    UPDATE: (id: string) => `/food-entries/${id}`,
    DELETE: (id: string) => `/food-entries/${id}`,
  },
  
  // Analytics
  ANALYTICS: {
    SUMMARY: '/analytics/summary',
    TRENDS: '/analytics/trends',
  },
  
  // Profile
  PROFILE: {
    GET: '/profile',
    UPDATE: '/profile',
    DELETE: '/profile',
  },
} as const;

// Type definitions for API responses
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: string;
    timestamp: string;
    requestId: string;
  };
}

// Helper function to handle API errors
export const handleApiError = (error: any): string => {
  if (error.response?.data?.error?.message) {
    return error.response.data.error.message;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};