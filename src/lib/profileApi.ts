/**
 * Profile API client functions
 */

import { apiClient, handleApiError } from './api';
import type {
  ProfileResponse,
  ProfileUpdate,
  HealthMetricsHistoryResponse,
} from '../types/profile';

/**
 * Get current user profile
 * @returns Promise<ProfileResponse>
 */
export const getProfile = async (): Promise<ProfileResponse> => {
  try {
    const response = await apiClient.get<ProfileResponse>('/profile');
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Update user profile
 * @param data - Profile update data
 * @returns Promise<ProfileResponse>
 */
export const updateProfile = async (data: ProfileUpdate): Promise<ProfileResponse> => {
  try {
    const response = await apiClient.put<ProfileResponse>('/profile', data);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

/**
 * Get health metrics history with pagination
 * @param page - Page number (1-indexed)
 * @param pageSize - Number of items per page
 * @returns Promise<HealthMetricsHistoryResponse>
 */
export const getHealthMetricsHistory = async (
  page: number = 1,
  pageSize: number = 10
): Promise<HealthMetricsHistoryResponse> => {
  try {
    const response = await apiClient.get<HealthMetricsHistoryResponse>(
      '/profile/health-metrics-history',
      {
        params: { page, page_size: pageSize },
      }
    );
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};
