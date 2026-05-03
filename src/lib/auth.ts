/**
 * Authentication service utilities
 */

import { apiClient, API_ENDPOINTS } from './api';

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
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  is_first_login: boolean;
}

export interface UserInfo {
  user_id: string;
  email: string;
  name: string;
  created_at: string;
  last_login: string | null;
  first_login_completed: boolean;
}

/**
 * Login user with email and password
 */
export const loginUser = async (data: LoginRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>(API_ENDPOINTS.AUTH.LOGIN, data);
  return response.data;
};

/**
 * Register a new user
 */
export const signupUser = async (data: SignupRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>(API_ENDPOINTS.AUTH.SIGNUP, data);
  return response.data;
};

/**
 * Logout current user
 */
export const logoutUser = async (): Promise<void> => {
  await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
};

/**
 * Refresh authentication token
 */
export const refreshAuthToken = async (): Promise<{ access_token: string; token_type: string; expires_in: number }> => {
  const response = await apiClient.post(API_ENDPOINTS.AUTH.REFRESH);
  return response.data;
};

/**
 * Get current user information
 */
export const getCurrentUser = async (): Promise<UserInfo> => {
  const response = await apiClient.get<UserInfo>(API_ENDPOINTS.AUTH.LOGIN.replace('/login', '/me'));
  return response.data;
};

/**
 * Validate password strength
 * Returns true if password meets all requirements
 */
export const validatePasswordStrength = (password: string): { valid: boolean; errors: string[] } => {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }

  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one digit');
  }

  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
};

/**
 * Validate email format
 */
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};
