import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient, API_ENDPOINTS, handleApiError } from '@/lib/api';

interface User {
  userId: string;
  email: string;
  name: string;
  isFirstLogin: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  refreshUserData: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          // Fetch current user info
          const response = await apiClient.get(API_ENDPOINTS.AUTH.LOGIN.replace('/login', '/me'));
          setUser({
            userId: response.data.user_id,
            email: response.data.email,
            name: response.data.name,
            isFirstLogin: !response.data.first_login_completed,
          });
        } catch (error) {
          // Token is invalid, clear it
          localStorage.removeItem('access_token');
          localStorage.removeItem('token_expires_at');
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  // Set up token refresh timer
  useEffect(() => {
    if (!user) return;

    const checkTokenExpiry = () => {
      const expiresAt = localStorage.getItem('token_expires_at');
      if (!expiresAt) return;

      const expiryTime = parseInt(expiresAt, 10);
      const now = Date.now();
      const timeUntilExpiry = expiryTime - now;

      // Refresh token 5 minutes before expiry
      if (timeUntilExpiry < 5 * 60 * 1000 && timeUntilExpiry > 0) {
        refreshToken();
      }
    };

    // Check every minute
    const interval = setInterval(checkTokenExpiry, 60 * 1000);
    return () => clearInterval(interval);
  }, [user]);

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, {
        email,
        password,
      });

      const { access_token, expires_in, user_id, is_first_login } = response.data;

      // Store token and expiry time
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('token_expires_at', String(Date.now() + expires_in * 1000));

      // Fetch user details
      const userResponse = await apiClient.get(API_ENDPOINTS.AUTH.LOGIN.replace('/login', '/me'));
      setUser({
        userId: user_id,
        email: userResponse.data.email,
        name: userResponse.data.name,
        isFirstLogin: is_first_login,
      });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  };

  const signup = async (name: string, email: string, password: string) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.SIGNUP, {
        name,
        email,
        password,
      });

      const { access_token, expires_in, user_id, is_first_login } = response.data;

      // Store token and expiry time
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('token_expires_at', String(Date.now() + expires_in * 1000));

      setUser({
        userId: user_id,
        email,
        name,
        isFirstLogin: is_first_login,
      });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  };

  const logout = async () => {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout error:', error);
    } finally {
      // Clear local storage and state
      localStorage.removeItem('access_token');
      localStorage.removeItem('token_expires_at');
      setUser(null);
    }
  };

  const refreshToken = async () => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.REFRESH);
      const { access_token, expires_in } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('token_expires_at', String(Date.now() + expires_in * 1000));
    } catch (error) {
      // If refresh fails, logout user
      await logout();
      throw new Error('Session expired. Please login again.');
    }
  };

  const refreshUserData = async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.AUTH.LOGIN.replace('/login', '/me'));
      setUser({
        userId: response.data.user_id,
        email: response.data.email,
        name: response.data.name,
        isFirstLogin: !response.data.first_login_completed,
      });
    } catch (error) {
      console.error('Failed to refresh user data:', error);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    signup,
    logout,
    refreshToken,
    refreshUserData,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
