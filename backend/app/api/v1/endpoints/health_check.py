"""
Health check API endpoints for diabetes prediction.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.health_metrics import HealthMetrics
from app.models.prediction import Prediction
from app.schemas.health_metrics import HealthMetricsCreate, HealthMetricsResponse
from app.schemas.prediction import PredictionResponse, PredictionWithMetrics
from app.services.diabetes_prediction_service import DiabetesPredictionService


router = APIRouter()


@router.post("/submit", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def submit_health_check(
    health_data: HealthMetricsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit health metrics and receive diabetes prediction.
    
    This endpoint:
    1. Validates and stores health metrics
    2. Loads the active ML model
    3. Generates a diabetes prediction
    4. Returns prediction with confidence score
    
    Args:
        health_data: Health metrics including weight, blood sugar, age, height, symptoms
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Prediction response with classification, confidence, and probabilities
    
    Raises:
        HTTPException 422: If health metrics are insufficient or invalid
        HTTPException 422: If ML model service is unavailable
        HTTPException 500: If prediction fails
    """
    try:
        # Create health metrics record
        health_metrics = HealthMetrics(
            user_id=current_user.user_id,
            weight_kg=health_data.weight_kg,
            blood_sugar_mgdl=health_data.blood_sugar_mgdl,
            age=health_data.age,
            height_cm=health_data.height_cm,
            symptoms=health_data.symptoms
        )
        
        # Calculate BMI manually since it's not a database default anymore
        height_m = float(health_data.height_cm) / 100.0
        health_metrics.bmi = round(float(health_data.weight_kg) / (height_m * height_m), 2)
        
        db.add(health_metrics)
        db.commit()
        db.refresh(health_metrics)
        
        # Initialize prediction service
        try:
            prediction_service = DiabetesPredictionService(db)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "MODEL_UNAVAILABLE",
                    "message": "ML prediction service is currently unavailable",
                    "details": str(e)
                }
            )
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "MODEL_UNAVAILABLE",
                    "message": "ML model file not found",
                    "details": str(e)
                }
            )
        
        # Generate prediction
        try:
            classification, confidence, probabilities = prediction_service.predict(health_metrics)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "PREDICTION_INSUFFICIENT_DATA",
                    "message": "Insufficient or invalid health metrics for prediction",
                    "details": str(e)
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "SERVER_ML_SERVICE_ERROR",
                    "message": "Prediction generation failed",
                    "details": str(e)
                }
            )
        
        # Create prediction record
        prediction = prediction_service.create_prediction_record(
            user_id=str(current_user.user_id),
            metric_id=str(health_metrics.metric_id),
            classification=classification,
            confidence=confidence,
            probabilities=probabilities
        )
        
        # Log prediction for monitoring
        prediction_service.log_prediction(prediction, health_metrics)
        
        # Update first_login_completed flag for first-time users
        if not current_user.first_login_completed:
            current_user.first_login_completed = True
            db.commit()
        
        # Return prediction response
        return PredictionResponse(
            prediction_id=str(prediction.prediction_id),
            user_id=str(prediction.user_id),
            metric_id=str(prediction.metric_id),
            model_version=prediction.model_version,
            classification=prediction.classification,
            confidence=float(prediction.confidence),
            probabilities=prediction.probabilities,
            predicted_at=prediction.predicted_at
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        db.rollback()
        raise
    except Exception as e:
        # Handle unexpected errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": str(e)
            }
        )


@router.get("/history", response_model=List[PredictionResponse])
async def get_prediction_history(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's prediction history.
    
    Args:
        limit: Maximum number of predictions to return (default: 10)
        offset: Number of predictions to skip (default: 0)
        current_user: Authenticated user
        db: Database session
    
    Returns:
        List of prediction records sorted by date (newest first)
    """
    predictions = db.query(Prediction).filter(
        Prediction.user_id == current_user.user_id
    ).order_by(
        Prediction.predicted_at.desc()
    ).limit(limit).offset(offset).all()
    
    return [
        PredictionResponse(
            prediction_id=str(pred.prediction_id),
            user_id=str(pred.user_id),
            metric_id=str(pred.metric_id),
            model_version=pred.model_version,
            classification=pred.classification,
            confidence=float(pred.confidence),
            probabilities=pred.probabilities,
            predicted_at=pred.predicted_at
        )
        for pred in predictions
    ]


@router.get("/latest", response_model=PredictionWithMetrics)
async def get_latest_prediction(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's most recent prediction with associated health metrics.
    
    Args:
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Latest prediction with health metrics
    
    Raises:
        HTTPException 404: If no predictions found for user
    """
    prediction = db.query(Prediction).filter(
        Prediction.user_id == current_user.user_id
    ).order_by(
        Prediction.predicted_at.desc()
    ).first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RESOURCE_NOT_FOUND",
                "message": "No predictions found for this user"
            }
        )
    
    # Get associated health metrics
    health_metrics = db.query(HealthMetrics).filter(
        HealthMetrics.metric_id == prediction.metric_id
    ).first()
    
    health_metrics_data = {
        "metric_id": str(health_metrics.metric_id),
        "weight_kg": float(health_metrics.weight_kg),
        "blood_sugar_mgdl": float(health_metrics.blood_sugar_mgdl),
        "age": health_metrics.age,
        "height_cm": float(health_metrics.height_cm),
        "bmi": float(health_metrics.bmi),
        "symptoms": health_metrics.symptoms,
        "recorded_at": health_metrics.recorded_at.isoformat()
    }
    
    return PredictionWithMetrics(
        prediction_id=str(prediction.prediction_id),
        user_id=str(prediction.user_id),
        classification=prediction.classification,
        confidence=float(prediction.confidence),
        probabilities=prediction.probabilities,
        predicted_at=prediction.predicted_at,
        model_version=prediction.model_version,
        health_metrics=health_metrics_data
    )


@router.get("/model-info")
async def get_model_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get information about the currently active ML model.
    
    Args:
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Model metadata including type, version, accuracy metrics
    """
    try:
        prediction_service = DiabetesPredictionService(db)
        model_info = prediction_service.get_model_info()
        return model_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ML_SERVICE_ERROR",
                "message": "Failed to retrieve model information",
                "details": str(e)
            }
        )


@router.get("/model-performance")
async def get_model_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get model performance metrics and alerts.
    
    This endpoint provides:
    - Rolling accuracy over recent predictions
    - Model age and version
    - Performance alerts (low accuracy, model age)
    
    Args:
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Performance metrics and alerts
    """
    try:
        prediction_service = DiabetesPredictionService(db)
        performance = prediction_service.check_model_performance()
        return performance
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ML_SERVICE_ERROR",
                "message": "Failed to retrieve model performance",
                "details": str(e)
            }
        )
