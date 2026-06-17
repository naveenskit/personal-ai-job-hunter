"""create scheduler_locks table

Revision ID: 0003_create_scheduler_locks
Revises: 0002_create_job_runs
Create Date: 2026-06-17 00:10:00.000000
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0003_create_scheduler_locks'
down_revision = '0002_create_job_runs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'scheduler_locks',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=120), nullable=False, unique=True),
        sa.Column('owner', sa.String(length=255), nullable=True),
        sa.Column('acquired_at', sa.String(length=40), nullable=True),
        sa.Column('expires_at', sa.String(length=40), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('scheduler_locks')
