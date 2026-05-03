"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')  # For trigram similarity search
    
    # Create users table
    op.create_table('users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('first_login_completed', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    
    # Create health_metrics table
    op.create_table('health_metrics',
        sa.Column('metric_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('weight_kg', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('blood_sugar_mgdl', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('height_cm', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('bmi', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('symptoms', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint('weight_kg BETWEEN 20 AND 300', name='weight_range'),
        sa.CheckConstraint('blood_sugar_mgdl BETWEEN 20 AND 600', name='blood_sugar_range'),
        sa.CheckConstraint('age BETWEEN 1 AND 120', name='age_range'),
        sa.CheckConstraint('height_cm BETWEEN 50 AND 250', name='height_range'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('metric_id')
    )
    op.create_index('idx_health_metrics_user', 'health_metrics', ['user_id', 'recorded_at'], unique=False)
    
    # Create predictions table
    op.create_table('predictions',
        sa.Column('prediction_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('classification', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('probabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('predicted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint("classification IN ('Type 1', 'Type 2', 'No Diabetes')", name='classification_values'),
        sa.CheckConstraint('confidence BETWEEN 0 AND 1', name='confidence_range'),
        sa.ForeignKeyConstraint(['metric_id'], ['health_metrics.metric_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('prediction_id')
    )
    op.create_index('idx_predictions_user', 'predictions', ['user_id', 'predicted_at'], unique=False)
    
    # Create foods table
    op.create_table('foods',
        sa.Column('food_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('food_type', sa.String(length=100), nullable=True),
        sa.Column('allergens', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('food_id')
    )
    # Create GIN index for full-text search on name
    op.execute("CREATE INDEX idx_foods_name_fts ON foods USING gin(to_tsvector('english', name))")
    # Create GIN index for trigram similarity search (for fuzzy matching)
    op.create_index('idx_foods_name_trgm', 'foods', ['name'], unique=False, postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})
    op.create_index('idx_foods_category', 'foods', ['category'], unique=False)
    
    # Create nutrients table
    op.create_table('nutrients',
        sa.Column('nutrient_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('nutrient_type', sa.String(length=50), nullable=False),
        sa.CheckConstraint("nutrient_type IN ('macronutrient', 'vitamin', 'mineral', 'other')", name='nutrient_type_values'),
        sa.PrimaryKeyConstraint('nutrient_id'),
        sa.UniqueConstraint('name')
    )
    
    # Create food_nutrients table
    op.create_table('food_nutrients',
        sa.Column('food_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nutrient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('per_unit', sa.String(length=20), nullable=False, default='100g'),
        sa.ForeignKeyConstraint(['food_id'], ['foods.food_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['nutrient_id'], ['nutrients.nutrient_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('food_id', 'nutrient_id')
    )
    op.create_index('idx_food_nutrients_food', 'food_nutrients', ['food_id'], unique=False)
    
    # Create food_entries table
    op.create_table('food_entries',
        sa.Column('entry_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('food_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('meal_type', sa.String(length=20), nullable=False),
        sa.Column('consumed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint("meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')", name='meal_type_values'),
        sa.CheckConstraint('quantity > 0', name='quantity_positive'),
        sa.ForeignKeyConstraint(['food_id'], ['foods.food_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('entry_id')
    )
    op.create_index('idx_food_entries_user_date', 'food_entries', ['user_id', 'consumed_at'], unique=False)
    op.create_index('idx_food_entries_meal_type', 'food_entries', ['user_id', 'meal_type'], unique=False)
    
    # Create user_profiles table
    op.create_table('user_profiles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('allergen_preferences', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('dietary_restrictions', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('health_conditions', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    # Create ml_model_metadata table
    op.create_table('ml_model_metadata',
        sa.Column('model_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_type', sa.String(length=50), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('accuracy', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('precision_type1', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('precision_type2', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('recall', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('f1_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('training_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=False),
        sa.Column('model_path', sa.String(length=500), nullable=False),
        sa.Column('feature_list', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint("model_type IN ('Logistic Regression', 'Random Forest', 'Neural Network')", name='model_type_values'),
        sa.PrimaryKeyConstraint('model_id'),
        sa.UniqueConstraint('version')
    )
    op.create_index('idx_ml_model_active', 'ml_model_metadata', ['is_active', 'version'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('ml_model_metadata')
    op.drop_table('user_profiles')
    op.drop_table('food_entries')
    op.drop_table('food_nutrients')
    op.drop_table('nutrients')
    op.drop_table('foods')
    op.drop_table('predictions')
    op.drop_table('health_metrics')
    op.drop_table('users')
    
    # Drop extensions
    op.execute('DROP EXTENSION IF EXISTS "pg_trgm"')
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')