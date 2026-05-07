"""update classification constraint for RF risk labels

Revision ID: 007
Revises: 006
Create Date: 2026-05-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """
    Update the classification_values constraint to support RF model risk labels.
    
    The new RF #2 (Risk Classifier) returns risk levels based on ADA 2024 guidelines:
    - 'Low': fasting glucose <100 mg/dL (normal)
    - 'Mid': fasting glucose 100-125 mg/dL (prediabetes)
    - 'High': fasting glucose ≥126 mg/dL (diabetes)
    
    We keep the old values for backward compatibility with existing predictions.
    """
    # Drop the old constraint
    op.drop_constraint('classification_values', 'predictions', type_='check')
    
    # Create the new constraint with RF risk labels included
    op.create_check_constraint(
        'classification_values',
        'predictions',
        "classification IN ('Type 1', 'Type 2', 'No Diabetes', 'Has Diabetes', 'Low', 'Mid', 'High')"
    )


def downgrade():
    """Revert to the previous constraint."""
    # Drop the new constraint
    op.drop_constraint('classification_values', 'predictions', type_='check')
    
    # Recreate the old constraint
    op.create_check_constraint(
        'classification_values',
        'predictions',
        "classification IN ('Type 1', 'Type 2', 'No Diabetes', 'Has Diabetes')"
    )
