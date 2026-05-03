"""add age and height to user profile

Revision ID: 003
Revises: 002
Create Date: 2026-05-03

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add age and height_cm columns to user_profiles table
    op.add_column('user_profiles', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('user_profiles', sa.Column('height_cm', sa.Numeric(precision=5, scale=2), nullable=True))


def downgrade():
    # Remove age and height_cm columns from user_profiles table
    op.drop_column('user_profiles', 'height_cm')
    op.drop_column('user_profiles', 'age')
