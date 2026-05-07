"""
Main API router for v1 endpoints.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, health_check, foods, food_entries, profile, analytics, model_performance, meal_risk, admin

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(health_check.router, prefix="/health-check", tags=["health-check"])
api_router.include_router(foods.router, prefix="/foods", tags=["foods"])
api_router.include_router(food_entries.router, prefix="/food-entries", tags=["food-entries"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(model_performance.router, prefix="/model-performance", tags=["model-performance"])
api_router.include_router(meal_risk.router, prefix="/meal-risk", tags=["meal-risk"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])


@api_router.get("/")
async def api_root():
    """API v1 root endpoint."""
    return {"message": "ML Diabetes Tracker API v1"}