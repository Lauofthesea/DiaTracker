"""
Health check API endpoints for diabetes prediction using RF models.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.health_metrics import HealthMetrics
from app.models.prediction import Prediction
from app.schemas.health_metrics import HealthMetricsCreate, HealthMetricsResponse
from app.schemas.prediction import PredictionResponse, PredictionWithMetrics
from app.services.rf_model_manager import RFModelManager


router = APIRouter()


@router.post("/submit", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def submit_health_check(
    health_data: HealthMetricsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit health metrics and receive diabetes prediction using RF #2 (Risk Classifier).
    
    This endpoint:
    1. Validates and stores health metrics
    2. Gets user profile for gender and family history
    3. Uses RF #2 model to generate risk prediction
    4. Returns prediction with confidence score
    
    Args:
        health_data: Health metrics including weight, blood sugar, age, height
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Prediction response with classification (Low/Mid/High), confidence, and probabilities
    
    Raises:
        HTTPException 404: If user profile not found
        HTTPException 422: If required profile data is missing
        HTTPException 500: If prediction fails
    """
    try:
        print(f"\n=== Health Check Submission (RF Model) ===")
        print(f"User: {current_user.email}")
        print(f"Data received: {health_data}")
        
        # Get user profile for gender and family history
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.user_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found. Please complete your profile first."
            )
        
        if not profile.gender:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Gender is required in your profile for risk assessment."
            )
        
        # Create health metrics record
        health_metrics = HealthMetrics(
            user_id=current_user.user_id,
            weight_kg=health_data.weight_kg,
            blood_sugar_mgdl=health_data.blood_sugar_mgdl,
            age=health_data.age,
            height_cm=health_data.height_cm,
            symptoms=health_data.symptoms
        )
        
        # Calculate BMI
        height_m = float(health_data.height_cm) / 100.0
        bmi = round(float(health_data.weight_kg) / (height_m * height_m), 2)
        health_metrics.bmi = bmi
        
        print(f"Health metrics: BMI={bmi}, Age={health_data.age}, Gender={profile.gender}")
        
        db.add(health_metrics)
        db.commit()
        db.refresh(health_metrics)
        
        print(f"Health metrics saved to database")
        
        # Initialize RF model manager
        try:
            print(f"Initializing RF model manager...")
            model_manager = RFModelManager()
            print(f"RF model manager initialized successfully")
        except Exception as e:
            print(f"Error initializing RF model manager: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"ML model service unavailable: {str(e)}"
            )
        
        # Prepare features for RF #2 (Risk Classifier)
        # Features: fasting_glucose, BMI, age, gender, family_history
        gender_encoded = 1 if profile.gender.lower() == 'female' else 0
        family_history_encoded = 1 if profile.family_history else 0
        
        features = {
            'fasting_glucose': float(health_data.blood_sugar_mgdl),
            'BMI': float(bmi),
            'age': int(health_data.age),
            'gender': gender_encoded,
            'family_history': family_history_encoded
        }
        
        print(f"Features for RF #2: {features}")
        
        # Generate prediction using RF #2
        try:
            print(f"Generating prediction with RF #2...")
            classification, confidence, probabilities = model_manager.predict_risk(features)
            print(f"Prediction: {classification}, Confidence: {confidence:.4f}")
            print(f"Probabilities: {probabilities}")
        except Exception as e:
            print(f"Error during prediction: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Prediction generation failed: {str(e)}"
            )
        
        # Create prediction record
        prediction = Prediction(
            user_id=current_user.user_id,
            metric_id=health_metrics.metric_id,
            model_version="2.0.0-rf",
            classification=classification,
            confidence=confidence,
            probabilities=probabilities
        )
        
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        print(f"Prediction saved to database")
        
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
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/history", response_model=List[PredictionWithMetrics])
async def get_prediction_history(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's prediction history with health metrics.
    
    Args:
        limit: Maximum number of predictions to return (default: 10)
        offset: Number of predictions to skip (default: 0)
        current_user: Authenticated user
        db: Database session
    
    Returns:
        List of prediction records with health metrics sorted by date (newest first)
    """
    predictions = db.query(Prediction).filter(
        Prediction.user_id == current_user.user_id
    ).order_by(
        Prediction.predicted_at.desc()
    ).limit(limit).offset(offset).all()
    
    result = []
    for pred in predictions:
        # Get associated health metrics
        metrics = db.query(HealthMetrics).filter(
            HealthMetrics.metric_id == pred.metric_id
        ).first()
        
        health_metrics_dict = {}
        if metrics:
            health_metrics_dict = {
                "weight_kg": float(metrics.weight_kg),
                "blood_sugar_mgdl": float(metrics.blood_sugar_mgdl),
                "age": metrics.age,
                "height_cm": float(metrics.height_cm),
                "bmi": float(metrics.bmi) if metrics.bmi else None,
                "symptoms": metrics.symptoms or []
            }
        
        result.append(
            PredictionWithMetrics(
                prediction_id=str(pred.prediction_id),
                user_id=str(pred.user_id),
                classification=pred.classification,
                confidence=float(pred.confidence),
                probabilities=pred.probabilities,
                predicted_at=pred.predicted_at,
                model_version=pred.model_version,
                health_metrics=health_metrics_dict
            )
        )
    
    return result


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
    Get information about the currently active RF models.
    
    Args:
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Model metadata for both RF #1 and RF #2
    """
    try:
        model_manager = RFModelManager()
        model_info = model_manager.get_model_info()
        return model_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model information: {str(e)}"
        )


@router.get("/model-performance")
async def get_model_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get RF model health status.
    
    Args:
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Health status for RF models
    """
    try:
        model_manager = RFModelManager()
        health_status = model_manager.validate_model_health()
        return health_status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model performance: {str(e)}"
        )
