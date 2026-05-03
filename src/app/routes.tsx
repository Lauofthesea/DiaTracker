import { createBrowserRouter } from "react-router";
import HomePage from "./components/HomePage";
import LogMealPage from "./components/LogMealPage";
import MealHistoryPage from "./components/MealHistoryPage";
import InsightsPage from "./components/InsightsPage";
import ProfilePage from "./components/ProfilePage";
import LoginPage from "./components/auth/LoginPage";
import SignupPage from "./components/auth/SignupPage";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import { HealthCheckPage } from "./components/health-check";

export const router = createBrowserRouter([
  // Public routes
  { path: "/login", Component: LoginPage },
  { path: "/signup", Component: SignupPage },
  
  // Protected routes
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <HomePage />
      </ProtectedRoute>
    ),
  },
  {
    path: "/health-check",
    element: (
      <ProtectedRoute>
        <HealthCheckPage />
      </ProtectedRoute>
    ),
  },
  {
    path: "/log-meal",
    element: (
      <ProtectedRoute>
        <LogMealPage />
      </ProtectedRoute>
    ),
  },
  {
    path: "/history",
    element: (
      <ProtectedRoute>
        <MealHistoryPage />
      </ProtectedRoute>
    ),
  },
  {
    path: "/insights",
    element: (
      <ProtectedRoute>
        <InsightsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: "/profile",
    element: (
      <ProtectedRoute>
        <ProfilePage />
      </ProtectedRoute>
    ),
  },
  
  // Catch-all redirect to home
  {
    path: "*",
    element: (
      <ProtectedRoute>
        <HomePage />
      </ProtectedRoute>
    ),
  },
]);
