"""Add meal predictions table

Revision ID: 008
Revises: 007
Create Date: 2026-05-07 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create meal_predictions table
    op.create_table(
        'meal_predictions',
        sa.Column('prediction_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('food_entry_id', sa.UUID(), nullable=True),
        sa.Column('fasting_glucose', sa.Float(), nullable=False),
        sa.Column('available_carbs_g', sa.Float(), nullable=False),
        sa.Column('fat_g', sa.Float(), nullable=False),
        sa.Column('protein_g', sa.Float(), nullable=False),
        sa.Column('fiber_g', sa.Float(), nullable=False),
        sa.Column('bmi', sa.Float(), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('gender', sa.Integer(), nullable=False),
        sa.Column('predicted_glucose_1hr', sa.Float(), nullable=False),
        sa.Column('confidence_lower', sa.Float(), nullable=True),
        sa.Column('confidence_upper', sa.Float(), nullable=True),
        sa.Column('risk_level', sa.String(10), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('predicted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('prediction_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['food_entry_id'], ['food_entries.entry_id'], ondelete='SET NULL'),
        sa.CheckConstraint("risk_level IN ('Low', 'Mid', 'High')", name='meal_predictions_risk_level_check')
    )
    
    # Create indexes
    op.create_index('ix_meal_predictions_user_id', 'meal_predictions', ['user_id'])
    op.create_index('ix_meal_predictions_predicted_at', 'meal_predictions', ['predicted_at'])
    op.create_index('ix_meal_predictions_risk_level', 'meal_predictions', ['risk_level'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_meal_predictions_risk_level', table_name='meal_predictions')
    op.drop_index('ix_meal_predictions_predicted_at', table_name='meal_predictions')
    op.drop_index('ix_meal_predictions_user_id', table_name='meal_predictions')
    
    # Drop table
    op.drop_table('meal_predictions')
