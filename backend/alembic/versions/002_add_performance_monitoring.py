"""Add performance monitoring tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create prediction_logs table for detailed monitoring
    op.create_table('prediction_logs',
        sa.Column('log_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('prediction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('input_features', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('predicted_class', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('probabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('ground_truth', sa.String(length=50), nullable=True),  # Actual diagnosis (if available)
        sa.Column('is_correct', sa.Boolean(), nullable=True),  # Whether prediction matched ground truth
        sa.Column('logged_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['prediction_id'], ['predictions.prediction_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index('idx_prediction_logs_model_version', 'prediction_logs', ['model_version', 'logged_at'], unique=False)
    op.create_index('idx_prediction_logs_ground_truth', 'prediction_logs', ['ground_truth'], unique=False)
    
    # Create model_performance_metrics table for aggregated metrics
    op.create_table('model_performance_metrics',
        sa.Column('metric_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('window_size', sa.Integer(), nullable=False),  # Number of predictions in window
        sa.Column('accuracy', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('precision_type1', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('precision_type2', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('precision_no_diabetes', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('recall_type1', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('recall_type2', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('recall_no_diabetes', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('f1_type1', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('f1_type2', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('f1_no_diabetes', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('confusion_matrix', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('total_predictions', sa.Integer(), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('metric_id')
    )
    op.create_index('idx_model_performance_version', 'model_performance_metrics', ['model_version', 'calculated_at'], unique=False)
    
    # Create model_performance_alerts table
    op.create_table('model_performance_alerts',
        sa.Column('alert_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('metric_value', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('threshold_value', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("alert_type IN ('LOW_ACCURACY', 'LOW_PRECISION', 'LOW_RECALL', 'MODEL_AGE', 'DRIFT_DETECTED', 'RETRAINING_NEEDED')", name='alert_type_values'),
        sa.CheckConstraint("severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name='severity_values'),
        sa.PrimaryKeyConstraint('alert_id')
    )
    op.create_index('idx_alerts_model_version', 'model_performance_alerts', ['model_version', 'is_resolved'], unique=False)
    op.create_index('idx_alerts_created', 'model_performance_alerts', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('model_performance_alerts')
    op.drop_table('model_performance_metrics')
    op.drop_table('prediction_logs')
