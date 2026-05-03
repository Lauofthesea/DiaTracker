"""
Model performance monitoring service for ML model tracking and alerting.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.models.prediction_log import PredictionLog, ModelPerformanceMetrics, ModelPerformanceAlert
from app.models.prediction import Prediction
from app.models.health_metrics import HealthMetrics
from app.models.ml_model_metadata import MLModelMetadata


class ModelPerformanceService:
    """Service for monitoring ML model performance and generating alerts."""
    
    def __init__(self, db: Session):
        """
        Initialize model performance service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def log_prediction(
        self,
        prediction: Prediction,
        health_metrics: HealthMetrics,
        ground_truth: Optional[str] = None
    ) -> PredictionLog:
        """
        Log prediction with inputs and outputs for performance monitoring.
        
        Args:
            prediction: Prediction object
            health_metrics: Health metrics used for prediction
            ground_truth: Actual diagnosis (if available)
        
        Returns:
            Created PredictionLog object
        """
        # Prepare input features
        input_features = {
            'weight_kg': float(health_metrics.weight_kg),
            'blood_sugar_mgdl': float(health_metrics.blood_sugar_mgdl),
            'age': health_metrics.age,
            'bmi': float(health_metrics.bmi),
            'height_cm': float(health_metrics.height_cm),
            'symptoms': health_metrics.symptoms if health_metrics.symptoms else []
        }
        
        # Determine if prediction is correct (if ground truth available)
        is_correct = None
        if ground_truth:
            is_correct = (prediction.classification == ground_truth)
        
        # Create prediction log
        log = PredictionLog(
            prediction_id=prediction.prediction_id,
            user_id=prediction.user_id,
            model_version=prediction.model_version,
            input_features=input_features,
            predicted_class=prediction.classification,
            confidence=prediction.confidence,
            probabilities=prediction.probabilities,
            ground_truth=ground_truth,
            is_correct=is_correct
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def update_ground_truth(
        self,
        prediction_id: str,
        ground_truth: str
    ) -> Optional[PredictionLog]:
        """
        Update ground truth for a prediction (e.g., when actual diagnosis is confirmed).
        
        Args:
            prediction_id: Prediction ID
            ground_truth: Actual diagnosis
        
        Returns:
            Updated PredictionLog or None if not found
        """
        log = self.db.query(PredictionLog).filter(
            PredictionLog.prediction_id == prediction_id
        ).first()
        
        if not log:
            return None
        
        log.ground_truth = ground_truth
        log.is_correct = (log.predicted_class == ground_truth)
        
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def calculate_rolling_accuracy(
        self,
        model_version: Optional[str] = None,
        window_size: int = 1000
    ) -> Optional[float]:
        """
        Calculate rolling accuracy over recent predictions with ground truth.
        
        Args:
            model_version: Specific model version (None for active model)
            window_size: Number of recent predictions to consider
        
        Returns:
            Rolling accuracy (0-1) or None if insufficient data
        """
        # Build query
        query = self.db.query(PredictionLog).filter(
            PredictionLog.ground_truth.isnot(None)
        )
        
        if model_version:
            query = query.filter(PredictionLog.model_version == model_version)
        
        # Get recent predictions with ground truth
        recent_logs = query.order_by(
            desc(PredictionLog.logged_at)
        ).limit(window_size).all()
        
        if len(recent_logs) < 100:
            # Not enough data for meaningful accuracy calculation
            return None
        
        # Calculate accuracy
        correct_predictions = sum(1 for log in recent_logs if log.is_correct)
        accuracy = correct_predictions / len(recent_logs)
        
        return accuracy
    
    def calculate_confusion_matrix(
        self,
        model_version: Optional[str] = None,
        window_size: int = 1000
    ) -> Optional[Dict]:
        """
        Generate confusion matrix for prediction accuracy analysis.
        
        Args:
            model_version: Specific model version (None for active model)
            window_size: Number of recent predictions to consider
        
        Returns:
            Confusion matrix as dictionary or None if insufficient data
        """
        # Build query
        query = self.db.query(PredictionLog).filter(
            PredictionLog.ground_truth.isnot(None)
        )
        
        if model_version:
            query = query.filter(PredictionLog.model_version == model_version)
        
        # Get recent predictions with ground truth
        recent_logs = query.order_by(
            desc(PredictionLog.logged_at)
        ).limit(window_size).all()
        
        if len(recent_logs) < 100:
            return None
        
        # Initialize confusion matrix
        classes = ['Type 1', 'Type 2', 'No Diabetes']
        matrix = {
            'classes': classes,
            'matrix': [[0 for _ in classes] for _ in classes],
            'total': len(recent_logs)
        }
        
        # Populate confusion matrix
        class_to_idx = {cls: idx for idx, cls in enumerate(classes)}
        
        for log in recent_logs:
            true_idx = class_to_idx.get(log.ground_truth)
            pred_idx = class_to_idx.get(log.predicted_class)
            
            if true_idx is not None and pred_idx is not None:
                matrix['matrix'][true_idx][pred_idx] += 1
        
        return matrix
    
    def calculate_precision_recall_f1(
        self,
        model_version: Optional[str] = None,
        window_size: int = 1000
    ) -> Optional[Dict]:
        """
        Calculate precision, recall, and F1 score for each class.
        
        Args:
            model_version: Specific model version (None for active model)
            window_size: Number of recent predictions to consider
        
        Returns:
            Dictionary with metrics per class or None if insufficient data
        """
        confusion_matrix = self.calculate_confusion_matrix(model_version, window_size)
        
        if not confusion_matrix:
            return None
        
        classes = confusion_matrix['classes']
        matrix = confusion_matrix['matrix']
        
        metrics = {}
        
        for idx, cls in enumerate(classes):
            # True positives: diagonal element
            tp = matrix[idx][idx]
            
            # False positives: sum of column excluding diagonal
            fp = sum(matrix[i][idx] for i in range(len(classes)) if i != idx)
            
            # False negatives: sum of row excluding diagonal
            fn = sum(matrix[idx][j] for j in range(len(classes)) if j != idx)
            
            # Calculate precision
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            
            # Calculate recall
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            
            # Calculate F1 score
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            metrics[cls] = {
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'true_positives': tp,
                'false_positives': fp,
                'false_negatives': fn
            }
        
        return metrics
    
    def save_performance_metrics(
        self,
        model_version: str,
        window_size: int = 1000
    ) -> Optional[ModelPerformanceMetrics]:
        """
        Calculate and save aggregated performance metrics.
        
        Args:
            model_version: Model version
            window_size: Number of recent predictions to consider
        
        Returns:
            Created ModelPerformanceMetrics object or None if insufficient data
        """
        # Calculate metrics
        accuracy = self.calculate_rolling_accuracy(model_version, window_size)
        confusion_matrix = self.calculate_confusion_matrix(model_version, window_size)
        class_metrics = self.calculate_precision_recall_f1(model_version, window_size)
        
        if accuracy is None or confusion_matrix is None or class_metrics is None:
            return None
        
        # Count total predictions with ground truth
        total_predictions = self.db.query(func.count(PredictionLog.log_id)).filter(
            and_(
                PredictionLog.model_version == model_version,
                PredictionLog.ground_truth.isnot(None)
            )
        ).scalar()
        
        # Create performance metrics record
        metrics = ModelPerformanceMetrics(
            model_version=model_version,
            window_size=window_size,
            accuracy=accuracy,
            precision_type1=class_metrics.get('Type 1', {}).get('precision'),
            precision_type2=class_metrics.get('Type 2', {}).get('precision'),
            precision_no_diabetes=class_metrics.get('No Diabetes', {}).get('precision'),
            recall_type1=class_metrics.get('Type 1', {}).get('recall'),
            recall_type2=class_metrics.get('Type 2', {}).get('recall'),
            recall_no_diabetes=class_metrics.get('No Diabetes', {}).get('recall'),
            f1_type1=class_metrics.get('Type 1', {}).get('f1_score'),
            f1_type2=class_metrics.get('Type 2', {}).get('f1_score'),
            f1_no_diabetes=class_metrics.get('No Diabetes', {}).get('f1_score'),
            confusion_matrix=confusion_matrix,
            total_predictions=total_predictions
        )
        
        self.db.add(metrics)
        self.db.commit()
        self.db.refresh(metrics)
        
        return metrics
    
    def create_alert(
        self,
        model_version: str,
        alert_type: str,
        severity: str,
        message: str,
        metric_value: Optional[float] = None,
        threshold_value: Optional[float] = None
    ) -> ModelPerformanceAlert:
        """
        Create a performance alert.
        
        Args:
            model_version: Model version
            alert_type: Type of alert (LOW_ACCURACY, LOW_PRECISION, etc.)
            severity: Alert severity (LOW, MEDIUM, HIGH, CRITICAL)
            message: Alert message
            metric_value: Current metric value
            threshold_value: Threshold that was crossed
        
        Returns:
            Created ModelPerformanceAlert object
        """
        alert = ModelPerformanceAlert(
            model_version=model_version,
            alert_type=alert_type,
            severity=severity,
            message=message,
            metric_value=metric_value,
            threshold_value=threshold_value,
            is_resolved=False
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def check_performance_thresholds(
        self,
        model_version: Optional[str] = None,
        window_size: int = 1000
    ) -> List[ModelPerformanceAlert]:
        """
        Check performance metrics against thresholds and generate alerts.
        
        Args:
            model_version: Specific model version (None for active model)
            window_size: Number of recent predictions to consider
        
        Returns:
            List of generated alerts
        """
        if not model_version:
            # Get active model
            active_model = self.db.query(MLModelMetadata).filter(
                MLModelMetadata.is_active == True
            ).first()
            
            if not active_model:
                return []
            
            model_version = active_model.version
        
        alerts = []
        
        # Calculate metrics
        accuracy = self.calculate_rolling_accuracy(model_version, window_size)
        class_metrics = self.calculate_precision_recall_f1(model_version, window_size)
        
        # Check accuracy threshold (80%)
        if accuracy is not None and accuracy < 0.80:
            alert = self.create_alert(
                model_version=model_version,
                alert_type='LOW_ACCURACY',
                severity='HIGH',
                message=f'Model accuracy has dropped to {accuracy:.2%}. Retraining recommended.',
                metric_value=accuracy,
                threshold_value=0.80
            )
            alerts.append(alert)
        
        # Check precision thresholds (80% for Type 1 and Type 2)
        if class_metrics:
            for cls in ['Type 1', 'Type 2']:
                precision = class_metrics.get(cls, {}).get('precision', 0)
                if precision < 0.80:
                    alert = self.create_alert(
                        model_version=model_version,
                        alert_type='LOW_PRECISION',
                        severity='HIGH',
                        message=f'{cls} precision has dropped to {precision:.2%}. Review model performance.',
                        metric_value=precision,
                        threshold_value=0.80
                    )
                    alerts.append(alert)
            
            # Check recall threshold (75% for any diabetes detection)
            type1_recall = class_metrics.get('Type 1', {}).get('recall', 0)
            type2_recall = class_metrics.get('Type 2', {}).get('recall', 0)
            avg_diabetes_recall = (type1_recall + type2_recall) / 2
            
            if avg_diabetes_recall < 0.75:
                alert = self.create_alert(
                    model_version=model_version,
                    alert_type='LOW_RECALL',
                    severity='CRITICAL',
                    message=f'Diabetes detection recall has dropped to {avg_diabetes_recall:.2%}. Immediate attention required.',
                    metric_value=avg_diabetes_recall,
                    threshold_value=0.75
                )
                alerts.append(alert)
        
        # Check model age
        model_metadata = self.db.query(MLModelMetadata).filter(
            MLModelMetadata.version == model_version
        ).first()
        
        if model_metadata:
            days_since_training = (datetime.utcnow() - model_metadata.training_date).days
            
            if days_since_training > 90:
                alert = self.create_alert(
                    model_version=model_version,
                    alert_type='MODEL_AGE',
                    severity='MEDIUM',
                    message=f'Model is {days_since_training} days old. Consider retraining with recent data.',
                    metric_value=days_since_training,
                    threshold_value=90
                )
                alerts.append(alert)
        
        return alerts
    
    def should_trigger_retraining(
        self,
        model_version: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        Determine if model retraining should be triggered.
        
        Args:
            model_version: Specific model version (None for active model)
        
        Returns:
            Tuple of (should_retrain, reasons)
        """
        if not model_version:
            # Get active model
            active_model = self.db.query(MLModelMetadata).filter(
                MLModelMetadata.is_active == True
            ).first()
            
            if not active_model:
                return False, []
            
            model_version = active_model.version
        
        reasons = []
        
        # Check for unresolved critical alerts
        critical_alerts = self.db.query(ModelPerformanceAlert).filter(
            and_(
                ModelPerformanceAlert.model_version == model_version,
                ModelPerformanceAlert.severity == 'CRITICAL',
                ModelPerformanceAlert.is_resolved == False
            )
        ).all()
        
        if critical_alerts:
            reasons.append(f'{len(critical_alerts)} critical performance alerts')
        
        # Check for multiple high severity alerts
        high_alerts = self.db.query(ModelPerformanceAlert).filter(
            and_(
                ModelPerformanceAlert.model_version == model_version,
                ModelPerformanceAlert.severity == 'HIGH',
                ModelPerformanceAlert.is_resolved == False
            )
        ).all()
        
        if len(high_alerts) >= 3:
            reasons.append(f'{len(high_alerts)} high severity alerts')
        
        # Check accuracy
        accuracy = self.calculate_rolling_accuracy(model_version)
        if accuracy is not None and accuracy < 0.75:
            reasons.append(f'Accuracy below 75% ({accuracy:.2%})')
        
        should_retrain = len(reasons) > 0
        
        return should_retrain, reasons
    
    def get_active_alerts(
        self,
        model_version: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[ModelPerformanceAlert]:
        """
        Get active (unresolved) alerts.
        
        Args:
            model_version: Filter by model version
            severity: Filter by severity
        
        Returns:
            List of active alerts
        """
        query = self.db.query(ModelPerformanceAlert).filter(
            ModelPerformanceAlert.is_resolved == False
        )
        
        if model_version:
            query = query.filter(ModelPerformanceAlert.model_version == model_version)
        
        if severity:
            query = query.filter(ModelPerformanceAlert.severity == severity)
        
        return query.order_by(desc(ModelPerformanceAlert.created_at)).all()
    
    def resolve_alert(self, alert_id: str) -> Optional[ModelPerformanceAlert]:
        """
        Mark an alert as resolved.
        
        Args:
            alert_id: Alert ID
        
        Returns:
            Updated alert or None if not found
        """
        alert = self.db.query(ModelPerformanceAlert).filter(
            ModelPerformanceAlert.alert_id == alert_id
        ).first()
        
        if not alert:
            return None
        
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def get_performance_summary(
        self,
        model_version: Optional[str] = None,
        window_size: int = 1000
    ) -> Dict:
        """
        Get comprehensive performance summary.
        
        Args:
            model_version: Specific model version (None for active model)
            window_size: Number of recent predictions to consider
        
        Returns:
            Dictionary with performance summary
        """
        if not model_version:
            # Get active model
            active_model = self.db.query(MLModelMetadata).filter(
                MLModelMetadata.is_active == True
            ).first()
            
            if active_model:
                model_version = active_model.version
        
        # Calculate metrics
        accuracy = self.calculate_rolling_accuracy(model_version, window_size)
        confusion_matrix = self.calculate_confusion_matrix(model_version, window_size)
        class_metrics = self.calculate_precision_recall_f1(model_version, window_size)
        
        # Get active alerts
        active_alerts = self.get_active_alerts(model_version)
        
        # Check retraining trigger
        should_retrain, retrain_reasons = self.should_trigger_retraining(model_version)
        
        # Get total predictions with ground truth
        total_with_ground_truth = self.db.query(func.count(PredictionLog.log_id)).filter(
            and_(
                PredictionLog.model_version == model_version,
                PredictionLog.ground_truth.isnot(None)
            )
        ).scalar() if model_version else 0
        
        return {
            'model_version': model_version,
            'window_size': window_size,
            'accuracy': accuracy,
            'confusion_matrix': confusion_matrix,
            'class_metrics': class_metrics,
            'active_alerts': [
                {
                    'alert_id': str(alert.alert_id),
                    'alert_type': alert.alert_type,
                    'severity': alert.severity,
                    'message': alert.message,
                    'metric_value': float(alert.metric_value) if alert.metric_value else None,
                    'threshold_value': float(alert.threshold_value) if alert.threshold_value else None,
                    'created_at': alert.created_at.isoformat()
                }
                for alert in active_alerts
            ],
            'should_retrain': should_retrain,
            'retrain_reasons': retrain_reasons,
            'total_predictions_with_ground_truth': total_with_ground_truth,
            'status': 'HEALTHY' if not should_retrain and len(active_alerts) == 0 else 'NEEDS_ATTENTION'
        }
