"""
Model performance monitoring API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.model_performance_service import ModelPerformanceService
from app.schemas.model_performance import (
    PerformanceSummaryResponse,
    AlertResponse,
    ConfusionMatrixResponse,
    GroundTruthUpdate,
    RetrainingCheckResponse
)


router = APIRouter()


@router.get("/summary", response_model=PerformanceSummaryResponse)
async def get_performance_summary(
    model_version: Optional[str] = None,
    window_size: int = Query(default=1000, ge=100, le=10000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive model performance summary.
    
    This endpoint provides:
    - Rolling accuracy over recent predictions
    - Confusion matrix
    - Precision, recall, and F1 scores per class
    - Active alerts
    - Retraining recommendations
    
    Args:
        model_version: Specific model version (None for active model)
        window_size: Number of recent predictions to consider (100-10000)
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Performance summary with metrics and alerts
    """
    try:
        performance_service = ModelPerformanceService(db)
        summary = performance_service.get_performance_summary(model_version, window_size)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ML_SERVICE_ERROR",
                "message": "Failed to retrieve performance summary",
                "details": str(e)
            }
        )


@router.get("/accuracy", response_model=dict)
async def get_rolling_accuracy(
    model_version: Optional[str] = None,
    window_size: int = Query(default=1000, ge=100, le=10000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get rolling accuracy over recent predictions.
    
    Args:
        model_version: Specific model version (None for active model)
        window_size: Number of recent predictions to consider
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Rolling accuracy metric
    """
    try:
        performance_service = ModelPerformanceService(db)
        accuracy = performance_service.calculate_rolling_accuracy(model_version, window_size)
        
        if accuracy is None:
            return {
                "accuracy": None,
                "message": "Insufficient data for accuracy calculation (minimum 100 predictions with ground truth required)",
                "window_size": window_size
            }
        
        return {
            "accuracy": accuracy,
            "window_size": window_size,
            "model_version": model_version,
            "threshold": 0.80,
            "status": "HEALTHY" if accuracy >= 0.80 else "BELOW_THRESHOLD"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ML_SERVICE_ERROR",
                "message": "Failed to calculate accuracy",
                "details": str(e)
            }
        )


@router.get("/confusion-matrix", response_model=ConfusionMatrixResponse)
async def get_confusion_matrix(
    model_version: Optional[str] = None,
    window_size: int = Query(default=1000, ge=100, le=10000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get confusion matrix for prediction accuracy analysis.
    
    Args:
        model_version: Specific model version (None for active model)
        window_size: Number of recent predictions to consider
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Confusion matrix with class labels
    """
    try:
        performance_service = ModelPerformanceService(db)
        confusion_matrix = performance_service.calculate_confusion_matrix(model_version, window_size)
        
        if confusion_matrix is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "INSUFFICIENT_DATA",
                    "message": "Insufficient data for confusion matrix (minimum 100 predictions with ground truth required)"
                }
            )
        
        return confusion_matrix
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ML_SERVICE_ERROR",
                "message": "Failed to generate confusion matrix",
                "details": str(e)
            }
        )


@router.get("/metrics", response_model=dict)
async def get_class_metrics(
    model_version: Optional[str] = None,
    window_size: int = Query(default=1000, ge=100, le=10000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get precision, recall, and F1 scores for each class.
    
    Args:
        model_version: Specific model version (None for active model)
        window_size: Number of recent predictions to consider
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Metrics per class (Type 1, Type 2, No Diabetes)
    """
    try:
        performance_service = ModelPerformanceService(db)
        class_metrics = performance_service.calculate_precision_recall_f1(model_version, window_size)
        
        if class_metrics is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "INSUFFICIENT_DATA",
                    "message": "Insufficient data for metrics calculation (minimum 100 predictions with ground truth required)"
                }
            )
        
        return {
            "model_version": model_version,
            "window_size": window_size,
            "metrics": class_metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ML_SERVICE_ERROR",
                "message": "Failed to calculate metrics",
                "details": str(e)
            }
        )


@router.get("/alerts", response_model=List[AlertResponse])
async def get_active_alerts(
    model_version: Optional[str] = None,
    severity: Optional[str] = Query(None, regex="^(LOW|MEDIUM|HIGH|CRITICAL)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get active (unresolved) performance alerts.
    
    Args:
        model_version: Filter by model version
        severity: Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
        current_user: Authenticated user
        db: Database session
    
    Returns:
        List of active alerts
    """
    try:
        performance_service = ModelPerformanceService(db)
        alerts = performance_service.get_active_alerts(model_version, severity)
        
        return [
            AlertResponse(
                alert_id=str(alert.alert_id),
                model_version=alert.model_version,
                alert_type=alert.alert_type,
                severity=alert.severity,
                message=alert.message,
                metric_value=float(alert.metric_value) if alert.metric_value else None,
                threshold_value=float(alert.threshold_value) if alert.threshold_value else None,
                is_resolved=alert.is_resolved,
                created_at=alert.created_at,
                resolved_at=alert.resolved_at
            )
            for alert in alerts
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ML_SERVICE_ERROR",
                "message": "Failed to retrieve alerts",
                "details": str(e)
            }
        )


@router.post("/alerts/check")
async def check_performance_thresholds(
    model_version: Optional[str] = None,
    window_size: int = Query(default=1000, ge=100, le=10000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check performance metrics against thresholds and generate alerts.
    
    This endpoint:
    - Calculates current performance metrics
    - Compares against defined thresholds
    - Creates alerts for threshold violations
    
    Args:
        model_version: Specific model version (None for active model)
        window_size: Number of recent predictions to consider
        current_user: Authenticated user
        db: Database session
    
    Returns:
        List of newly generated alerts
    """
    try:
        performance_service = ModelPerformanceService(db)
        alerts = performance_service.check_performance_thresholds(model_version, window_size)
        
        return {
            "alerts_generated": len(alerts),
            "alerts": [
                {
                    "alert_id": str(alert.alert_id),
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "metric_value": float(alert.metric_value) if alert.metric_value else None,
                    "threshold_value": float(alert.threshold_value) if alert.threshold_value else None
                }
                for alert in alerts
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ML_SERVICE_ERROR",
                "message": "Failed to check performance thresholds",
                "details": str(e)
            }
        )


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark an alert as resolved.
    
    Args:
        alert_id: Alert ID
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Updated alert
    """
    try:
        performance_service = ModelPerformanceService(db)
        alert = performance_service.resolve_alert(alert_id)
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "Alert not found"
                }
            )
        
        return {
            "alert_id": str(alert.alert_id),
            "is_resolved": alert.is_resolved,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ML_SERVICE_ERROR",
                "message": "Failed to resolve alert",
                "details": str(e)
            }
        )


@router.get("/retraining-check", response_model=RetrainingCheckResponse)
async def check_retraining_trigger(
    model_version: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if model retraining should be triggered.
    
    This endpoint evaluates:
    - Critical and high severity alerts
    - Accuracy thresholds
    - Model age
    
    Args:
        model_version: Specific model version (None for active model)
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Retraining recommendation with reasons
    """
    try:
        performance_service = ModelPerformanceService(db)
        should_retrain, reasons = performance_service.should_trigger_retraining(model_version)
        
        return RetrainingCheckResponse(
            should_retrain=should_retrain,
            reasons=reasons,
            model_version=model_version,
            recommendation="Immediate retraining recommended" if should_retrain else "Model performance is acceptable"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ML_SERVICE_ERROR",
                "message": "Failed to check retraining trigger",
                "details": str(e)
            }
        )


@router.post("/ground-truth/{prediction_id}")
async def update_ground_truth(
    prediction_id: str,
    ground_truth_data: GroundTruthUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update ground truth for a prediction (when actual diagnosis is confirmed).
    
    This endpoint allows updating predictions with actual diagnoses,
    which enables accurate performance monitoring.
    
    Args:
        prediction_id: Prediction ID
        ground_truth_data: Ground truth update data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Updated prediction log
    """
    try:
        performance_service = ModelPerformanceService(db)
        log = performance_service.update_ground_truth(
            prediction_id=prediction_id,
            ground_truth=ground_truth_data.ground_truth
        )
        
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "Prediction log not found"
                }
            )
        
        return {
            "log_id": str(log.log_id),
            "prediction_id": str(log.prediction_id),
            "ground_truth": log.ground_truth,
            "predicted_class": log.predicted_class,
            "is_correct": log.is_correct,
            "message": "Ground truth updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ML_SERVICE_ERROR",
                "message": "Failed to update ground truth",
                "details": str(e)
            }
        )


@router.post("/metrics/calculate")
async def calculate_and_save_metrics(
    model_version: str,
    window_size: int = Query(default=1000, ge=100, le=10000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate and save aggregated performance metrics.
    
    This endpoint calculates all performance metrics and stores them
    in the database for historical tracking.
    
    Args:
        model_version: Model version
        window_size: Number of recent predictions to consider
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Saved metrics record
    """
    try:
        performance_service = ModelPerformanceService(db)
        metrics = performance_service.save_performance_metrics(model_version, window_size)
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "INSUFFICIENT_DATA",
                    "message": "Insufficient data to calculate metrics (minimum 100 predictions with ground truth required)"
                }
            )
        
        return {
            "metric_id": str(metrics.metric_id),
            "model_version": metrics.model_version,
            "accuracy": float(metrics.accuracy) if metrics.accuracy else None,
            "window_size": metrics.window_size,
            "total_predictions": metrics.total_predictions,
            "calculated_at": metrics.calculated_at.isoformat(),
            "message": "Metrics calculated and saved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ML_SERVICE_ERROR",
                "message": "Failed to calculate metrics",
                "details": str(e)
            }
        )
