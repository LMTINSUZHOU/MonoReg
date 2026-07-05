"""add system settings

Revision ID: 0002_system_settings
Revises: 0001_initial
Create Date: 2026-07-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_system_settings"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def jsonb_type():
    return postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value_json", jsonb_type(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_system_settings_key", "system_settings", ["key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_system_settings_key", table_name="system_settings")
    op.drop_table("system_settings")
