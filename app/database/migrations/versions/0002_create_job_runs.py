"""create job_runs table

Revision ID: 0002_create_job_runs
Revises: 
Create Date: 2026-06-17 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0002_create_job_runs'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'job_runs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('job_name', sa.String(length=120), nullable=False),
        sa.Column('status', sa.String(length=40), nullable=False, server_default='running'),
        sa.Column('started_at', sa.String(length=40), nullable=False),
        sa.Column('finished_at', sa.String(length=40), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('processed_count', sa.Integer(), nullable=True),
        sa.Column('scored_count', sa.Integer(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('cancel_requested', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    op.drop_table('job_runs')
