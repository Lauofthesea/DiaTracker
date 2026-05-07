"""add weight and family history to user profile

Revision ID: 006
Revises: c3b59f52363c
Create Date: 2026-05-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = 'c3b59f52363c'
branch_labels = None
depends_on = None


def upgrade():
    # Add weight_kg column
    op.add_column('user_profiles', sa.Column('weight_kg', sa.Numeric(precision=5, scale=2), nullable=True))
    
    # Add family_history column
    op.add_column('user_profiles', sa.Column('family_history', sa.Boolean(), nullable=True, server_default='false'))


def downgrade():
    # Remove family_history column
    op.drop_column('user_profiles', 'family_history')
    
    # Remove weight_kg column
    op.drop_column('user_profiles', 'weight_kg')
