"""
Pydantic schemas for request/response validation.
"""

from app.schemas.auth import (
    UserRegistration,
    UserLogin,
    TokenResponse,
    TokenRefreshResponse,
    UserResponse
)
from app.schemas.health_metrics import (
    HealthMetricsCreate,
    HealthMetricsResponse,
    HealthMetricsUpdate,
    HealthMetricsHistory,
    SymptomsEncoded
)
from app.schemas.prediction import (
    PredictionCreate,
    PredictionResponse,
    PredictionHistory,
    PredictionWithMetrics
)
from app.schemas.profile import (
    ProfileResponse,
    ProfileUpdate,
    CurrentHealthMetrics,
    HealthMetricsHistoryItem,
    HealthMetricsHistoryResponse
)
from app.schemas.analytics import (
    MacronutrientDistribution,
    CarbohydrateWarning,
    PeriodSummaryResponse,
    DailyTrendData,
    NutritionalTrendsResponse
)

__all__ = [
    # Auth schemas
    "UserRegistration",
    "UserLogin",
    "TokenResponse",
    "TokenRefreshResponse",
    "UserResponse",
    # Health metrics schemas
    "HealthMetricsCreate",
    "HealthMetricsResponse",
    "HealthMetricsUpdate",
    "HealthMetricsHistory",
    "SymptomsEncoded",
    # Prediction schemas
    "PredictionCreate",
    "PredictionResponse",
    "PredictionHistory",
    "PredictionWithMetrics",
    # Profile schemas
    "ProfileResponse",
    "ProfileUpdate",
    "CurrentHealthMetrics",
    "HealthMetricsHistoryItem",
    "HealthMetricsHistoryResponse",
    # Analytics schemas
    "MacronutrientDistribution",
    "CarbohydrateWarning",
    "PeriodSummaryResponse",
    "DailyTrendData",
    "NutritionalTrendsResponse",
]