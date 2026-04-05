"""Add OTP table for password reset

Revision ID: 902c2146adec
Revises: 
Create Date: 2026-02-07 12:40:23.048250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '902c2146adec'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create OTP table
    op.create_table('otps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=6), nullable=False),
        sa.Column('purpose', sa.String(length=50), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop OTP table
    op.drop_table('otps')
