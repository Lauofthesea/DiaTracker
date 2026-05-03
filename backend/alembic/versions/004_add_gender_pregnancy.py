"""add gender and pregnancy to user profile

Revision ID: 004
Revises: 003
Create Date: 2026-05-03

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Add gender and is_pregnant columns to user_profiles table
    op.add_column('user_profiles', sa.Column('gender', sa.String(length=20), nullable=True))
    op.add_column('user_profiles', sa.Column('is_pregnant', sa.Boolean(), nullable=True, server_default='false'))


def downgrade():
    # Remove gender and is_pregnant columns from user_profiles table
    op.drop_column('user_profiles', 'is_pregnant')
    op.drop_column('user_profiles', 'gender')
