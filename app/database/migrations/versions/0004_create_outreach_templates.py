"""create outreach_templates table

Revision ID: 0004_create_outreach_templates
Revises: 0003_create_scheduler_locks
Create Date: 2026-06-17 00:20:00.000000
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0004_create_outreach_templates'
down_revision = '0003_create_scheduler_locks'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'outreach_templates',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=True),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('created_at', sa.String(length=40), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('outreach_templates')
