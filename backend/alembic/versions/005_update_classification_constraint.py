"""update classification constraint to include Has Diabetes

Revision ID: 005
Revises: 004
Create Date: 2026-05-03

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    """
    Update the classification_values constraint to include 'Has Diabetes'.
    
    The ML model returns binary classification ('No Diabetes' or 'Has Diabetes'),
    but the original constraint only allowed 'Type 1', 'Type 2', or 'No Diabetes'.
    """
    # Drop the old constraint
    op.drop_constraint('classification_values', 'predictions', type_='check')
    
    # Create the new constraint with 'Has Diabetes' included
    op.create_check_constraint(
        'classification_values',
        'predictions',
        "classification IN ('Type 1', 'Type 2', 'No Diabetes', 'Has Diabetes')"
    )


def downgrade():
    """Revert to the original constraint."""
    # Drop the new constraint
    op.drop_constraint('classification_values', 'predictions', type_='check')
    
    # Recreate the old constraint
    op.create_check_constraint(
        'classification_values',
        'predictions',
        "classification IN ('Type 1', 'Type 2', 'No Diabetes')"
    )
