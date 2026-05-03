import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/app/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import React from 'react';

// Mock the API client
vi.mock('@/lib/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
  API_ENDPOINTS: {
    AUTH: {
      LOGIN: '/auth/login',
      SIGNUP: '/auth/signup',
      LOGOUT: '/auth/logout',
      REFRESH: '/auth/refresh',
    },
  },
  handleApiError: vi.fn((error) => error.message || 'An error occurred'),
}));

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  describe('initialization', () => {
    it('should initialize with no user when no token in localStorage', async () => {
      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });

    it('should load user from token on initialization', async () => {
      localStorage.setItem('access_token', 'test-token');

      vi.mocked(apiClient.get).mockResolvedValueOnce({
        data: {
          user_id: '123',
          email: 'test@example.com',
          name: 'Test User',
          first_login_completed: true,
        },
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.user).toEqual({
        userId: '123',
        email: 'test@example.com',
        name: 'Test User',
        isFirstLogin: false,
      });
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('should clear invalid token on initialization', async () => {
      localStorage.setItem('access_token', 'invalid-token');

      vi.mocked(apiClient.get).mockRejectedValueOnce(new Error('Unauthorized'));

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(localStorage.getItem('access_token')).toBeNull();
    });
  });

  describe('login', () => {
    it('should login user successfully', async () => {
      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: {
          access_token: 'new-token',
          expires_in: 86400,
          user_id: '123',
          is_first_login: false,
        },
      });

      vi.mocked(apiClient.get).mockResolvedValueOnce({
        data: {
          user_id: '123',
          email: 'test@example.com',
          name: 'Test User',
          first_login_completed: true,
        },
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await result.current.login('test@example.com', 'password123');

      await waitFor(() => {
        expect(result.current.user).not.toBeNull();
      });

      expect(localStorage.getItem('access_token')).toBe('new-token');
      expect(result.current.user).toEqual({
        userId: '123',
        email: 'test@example.com',
        name: 'Test User',
        isFirstLogin: false,
      });
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('should handle login failure', async () => {
      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Invalid credentials'));

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await expect(result.current.login('test@example.com', 'wrong')).rejects.toThrow();
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('signup', () => {
    it('should signup user successfully', async () => {
      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: {
          access_token: 'new-token',
          expires_in: 86400,
          user_id: '123',
          is_first_login: true,
        },
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await result.current.signup('Test User', 'test@example.com', 'Password123!');

      await waitFor(() => {
        expect(result.current.user).not.toBeNull();
      });

      expect(localStorage.getItem('access_token')).toBe('new-token');
      expect(result.current.user).toEqual({
        userId: '123',
        email: 'test@example.com',
        name: 'Test User',
        isFirstLogin: true,
      });
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('should handle signup failure', async () => {
      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Email already exists'));

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await expect(
        result.current.signup('Test User', 'test@example.com', 'Password123!')
      ).rejects.toThrow();
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('logout', () => {
    it('should logout user successfully', async () => {
      localStorage.setItem('access_token', 'test-token');

      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { success: true } });

      const { result } = renderHook(() => useAuth(), { wrapper });

      // Set up authenticated user
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await result.current.logout();

      expect(localStorage.getItem('access_token')).toBeNull();
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });

    it('should clear local state even if API call fails', async () => {
      localStorage.setItem('access_token', 'test-token');

      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await result.current.logout();

      expect(localStorage.getItem('access_token')).toBeNull();
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('refreshToken', () => {
    it('should refresh token successfully', async () => {
      localStorage.setItem('access_token', 'old-token');

      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: {
          access_token: 'new-token',
          expires_in: 86400,
        },
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await result.current.refreshToken();

      expect(localStorage.getItem('access_token')).toBe('new-token');
    });

    it('should logout user if refresh fails', async () => {
      localStorage.setItem('access_token', 'old-token');

      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Token expired'));

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await expect(result.current.refreshToken()).rejects.toThrow();
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(result.current.user).toBeNull();
    });
  });
});
