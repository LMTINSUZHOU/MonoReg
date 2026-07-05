"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def jsonb_type():
    return postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="admin"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_admin_users_username", "admin_users", ["username"], unique=True)
    op.create_index("ix_admin_users_email", "admin_users", ["email"], unique=True)

    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("max_registrations", sa.Integer(), nullable=True),
        sa.Column("need_account", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("auto_generate_account", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("send_confirm_email", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("send_account_email_immediately", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("login_url", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_activities_slug", "activities", ["slug"], unique=True)
    op.create_index("ix_activities_status", "activities", ["status"])

    op.create_table(
        "form_fields",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("activity_id", sa.Integer(), sa.ForeignKey("activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_key", sa.String(length=128), nullable=False),
        sa.Column("field_label", sa.String(length=255), nullable=False),
        sa.Column("field_type", sa.String(length=64), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("placeholder", sa.Text(), nullable=True),
        sa.Column("help_text", sa.Text(), nullable=True),
        sa.Column("options_json", jsonb_type(), nullable=False, server_default="[]"),
        sa.Column("validation_json", jsonb_type(), nullable=False, server_default="{}"),
        sa.Column("show_in_table", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("activity_id", "field_key", name="uq_form_fields_activity_key"),
    )
    op.create_index("ix_form_fields_activity_id", "form_fields", ["activity_id"])

    op.create_table(
        "registrations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("activity_id", sa.Integer(), sa.ForeignKey("activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="pending"),
        sa.Column("form_data", jsonb_type(), nullable=False, server_default="{}"),
        sa.Column("submitted_ip", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("activity_id", "email", name="uq_registrations_activity_email"),
    )
    op.create_index("idx_registrations_activity_id", "registrations", ["activity_id"])
    op.create_index("idx_registrations_email", "registrations", ["email"])
    op.create_index("idx_registrations_status", "registrations", ["status"])
    op.create_index("idx_registrations_form_data", "registrations", ["form_data"], postgresql_using="gin")

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("activity_id", sa.Integer(), sa.ForeignKey("activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("registration_id", sa.Integer(), sa.ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password_encrypted", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ready"),
        sa.Column("generated_by", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("activity_id", "username", name="uq_accounts_activity_username"),
        sa.UniqueConstraint("registration_id", name="uq_accounts_registration_id"),
    )
    op.create_index("ix_accounts_activity_id", "accounts", ["activity_id"])
    op.create_index("ix_accounts_registration_id", "accounts", ["registration_id"])
    op.create_index("ix_accounts_status", "accounts", ["status"])

    op.create_table(
        "email_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("activity_id", sa.Integer(), sa.ForeignKey("activities.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_email_templates_activity_id", "email_templates", ["activity_id"])
    op.create_index("ix_email_templates_type", "email_templates", ["type"])

    op.create_table(
        "email_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("activity_id", sa.Integer(), sa.ForeignKey("activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("email_templates.id"), nullable=True),
        sa.Column("job_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("total_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("success_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_email_jobs_activity_id", "email_jobs", ["activity_id"])
    op.create_index("ix_email_jobs_status", "email_jobs", ["status"])

    op.create_table(
        "email_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("email_jobs.id", ondelete="CASCADE"), nullable=True),
        sa.Column("activity_id", sa.Integer(), sa.ForeignKey("activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("registration_id", sa.Integer(), sa.ForeignKey("registrations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("to_email", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("body_snapshot", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_email_logs_job_id", "email_logs", ["job_id"])
    op.create_index("idx_email_logs_status", "email_logs", ["status"])
    op.create_index("ix_email_logs_activity_id", "email_logs", ["activity_id"])
    op.create_index("ix_email_logs_registration_id", "email_logs", ["registration_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("resource_type", sa.String(length=128), nullable=True),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("detail_json", jsonb_type(), nullable=False, server_default="{}"),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_admin_id", "audit_logs", ["admin_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("email_logs")
    op.drop_table("email_jobs")
    op.drop_table("email_templates")
    op.drop_table("accounts")
    op.drop_table("registrations")
    op.drop_table("form_fields")
    op.drop_table("activities")
    op.drop_table("admin_users")

