"""
Meal Risk API Endpoints - Meal-based glucose prediction.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services.meal_risk_service import MealRiskService
from app.services.rf_model_manager import RFModelManager
from app.schemas.meal_risk import (
    MealRiskRequest,
    MealRiskResponse,
    MealHistoryResponse,
    ModelInfoResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/predict", response_model=MealRiskResponse, status_code=status.HTTP_200_OK)
async def predict_meal_risk(
    request: MealRiskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Predict glucose response to a meal.
    
    This endpoint uses the Glucose Predictor (RF #1) to predict 1-hour post-meal
    glucose levels based on meal composition and user profile data.
    
    **Required meal composition:**
    - available_carbs_g: Available carbohydrates (0-500g)
    - fat_g: Fat content (0-200g)
    - protein_g: Protein content (0-200g)
    - fiber_g: Fiber content (0-100g)
    
    **Optional parameters:**
    - fasting_glucose: Current fasting glucose (50-400 mg/dL, defaults to 100)
    - food_entry_id: Link prediction to a food entry
    
    **Returns:**
    - Predicted 1-hour post-meal glucose
    - 95% confidence interval
    - Risk classification (Low/Mid/High)
    - Human-readable explanation
    """
    try:
        # Get user profile for weight, height, age, gender, family_history
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.user_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found. Please complete your profile first."
            )
        
        # Validate profile has required fields
        if profile.weight_kg is None or profile.height_cm is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Weight and height are required in your profile for meal risk prediction."
            )
        
        if profile.age is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Age is required in your profile for meal risk prediction."
            )
        
        # Calculate BMI from weight and height
        height_m = float(profile.height_cm) / 100
        bmi = float(profile.weight_kg) / (height_m ** 2)
        
        # Encode gender (only Male=0, Female=1 supported)
        gender_map = {'male': 0, 'female': 1}
        gender = gender_map.get(profile.gender.lower() if profile.gender else 'male', 0)
        
        # Create meal risk service
        meal_service = MealRiskService(db)
        
        # Generate prediction
        result = meal_service.predict_meal_risk(
            user_id=str(current_user.user_id),
            fasting_glucose=request.fasting_glucose,
            available_carbs_g=request.available_carbs_g,
            fat_g=request.fat_g,
            protein_g=request.protein_g,
            fiber_g=request.fiber_g,
            bmi=bmi,
            age=profile.age,
            gender=gender,
            food_entry_id=request.food_entry_id
        )
        
        logger.info(
            f"Meal risk prediction generated for user {current_user.user_id}: "
            f"{result['predicted_glucose_1hr']:.1f} mg/dL ({result['risk_level']})"
        )
        
        return MealRiskResponse(**result)
    
    except ValueError as e:
        logger.error(f"Validation error in meal risk prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in meal risk prediction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while predicting meal risk. Please try again."
        )


@router.get("/history", response_model=MealHistoryResponse, status_code=status.HTTP_200_OK)
async def get_meal_history(
    start_date: Optional[str] = Query(None, description="Start date (ISO 8601)"),
    end_date: Optional[str] = Query(None, description="End date (ISO 8601)"),
    risk_level: Optional[str] = Query(None, pattern="^(Low|Mid|High)$", description="Filter by risk level"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve meal prediction history.
    
    Returns paginated list of previous meal risk predictions for the current user.
    
    **Query parameters:**
    - start_date: Filter predictions after this date (ISO 8601 format)
    - end_date: Filter predictions before this date (ISO 8601 format)
    - risk_level: Filter by risk level (Low, Mid, or High)
    - page: Page number (default: 1)
    - page_size: Results per page (default: 20, max: 100)
    
    **Returns:**
    - List of predictions with meal composition and results
    - Pagination metadata
    """
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use ISO 8601 format (e.g., 2026-05-06T10:00:00Z)"
                )
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use ISO 8601 format (e.g., 2026-05-06T10:00:00Z)"
                )
        
        # Create meal risk service
        meal_service = MealRiskService(db)
        
        # Get history
        result = meal_service.get_meal_history(
            user_id=str(current_user.user_id),
            start_date=start_dt,
            end_date=end_dt,
            risk_level=risk_level,
            page=page,
            page_size=page_size
        )
        
        logger.info(
            f"Retrieved {len(result['predictions'])} meal predictions for user {current_user.user_id} "
            f"(page {page}/{result['pagination']['total_pages']})"
        )
        
        return MealHistoryResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving meal history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving meal history. Please try again."
        )


@router.get("/models/info", response_model=ModelInfoResponse, status_code=status.HTTP_200_OK)
async def get_model_info():
    """
    Get information about loaded RF models.
    
    Returns metadata about the Glucose Predictor (RF #1) and Risk Classifier (RF #2),
    including versions, features, and load status.
    
    **Returns:**
    - Model versions
    - Feature lists
    - Load timestamps
    - Model status
    """
    try:
        model_manager = RFModelManager()
        info = model_manager.get_model_info()
        
        return ModelInfoResponse(**info)
    
    except Exception as e:
        logger.error(f"Error retrieving model info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving model information."
        )


@router.get("/models/health", status_code=status.HTTP_200_OK)
async def check_model_health():
    """
    Check health status of RF models.
    
    Returns health check status for both models.
    
    **Returns:**
    - glucose_predictor_loaded: Boolean
    - risk_classifier_loaded: Boolean
    - all_models_healthy: Boolean
    """
    try:
        model_manager = RFModelManager()
        health = model_manager.validate_model_health()
        
        if not health['all_models_healthy']:
            return {
                **health,
                "status": "degraded",
                "message": "One or more models are not loaded"
            }
        
        return {
            **health,
            "status": "healthy",
            "message": "All models loaded successfully"
        }
    
    except Exception as e:
        logger.error(f"Error checking model health: {str(e)}", exc_info=True)
        return {
            "glucose_predictor_loaded": False,
            "risk_classifier_loaded": False,
            "all_models_healthy": False,
            "status": "error",
            "message": str(e)
        }
