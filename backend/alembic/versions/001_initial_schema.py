"""Initial schema — whatsapp_groups, whatsapp_messages, events

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(conn, table_name: str) -> bool:
    result = conn.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :t)"),
        {"t": table_name},
    )
    return result.scalar()


def _index_exists(conn, index_name: str) -> bool:
    result = conn.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = :i)"),
        {"i": index_name},
    )
    return result.scalar()


def _create_enum_if_not_exists(conn, name: str, values: list[str]) -> None:
    result = conn.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = :n)"),
        {"n": name},
    )
    if not result.scalar():
        value_str = ", ".join(f"'{v}'" for v in values)
        conn.execute(sa.text(f"CREATE TYPE {name} AS ENUM ({value_str})"))


def _create_index_if_not_exists(conn, idx_name, table, columns, unique=False):
    if not _index_exists(conn, idx_name):
        op.create_index(idx_name, table, columns, unique=unique)


def upgrade() -> None:
    conn = op.get_bind()

    # Create enum types first
    _create_enum_if_not_exists(conn, "messagetype", ["text", "image", "audio", "video", "document", "location"])
    _create_enum_if_not_exists(conn, "messagesource", ["whatsapp_group", "manual_chat"])
    _create_enum_if_not_exists(conn, "eventtype", [
        "maintenance_request", "lease_inquiry", "payment_issue",
        "move_in", "move_out", "noise_complaint", "safety_concern",
        "amenity_request", "general_inquiry", "other",
    ])
    _create_enum_if_not_exists(conn, "priority", ["low", "medium", "high", "urgent"])
    _create_enum_if_not_exists(conn, "eventstatus", ["open", "in_progress", "resolved", "closed"])
    _create_enum_if_not_exists(conn, "eventsource", ["whatsapp_group", "manual_chat"])

    # whatsapp_groups
    if not _table_exists(conn, "whatsapp_groups"):
        op.create_table(
            "whatsapp_groups",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("group_id", sa.String(100), nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
    _create_index_if_not_exists(conn, "uq_whatsapp_groups_group_id", "whatsapp_groups", ["group_id"], unique=True)

    # whatsapp_messages
    if not _table_exists(conn, "whatsapp_messages"):
        op.create_table(
            "whatsapp_messages",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("whatsapp_message_id", sa.String(100), nullable=False),
            sa.Column("group_id", sa.String(100), sa.ForeignKey("whatsapp_groups.group_id", ondelete="SET NULL"), nullable=True),
            sa.Column("sender_id", sa.String(100), nullable=False),
            sa.Column("sender_name", sa.String(255), nullable=True),
            sa.Column(
                "message_type",
                postgresql.ENUM("text", "image", "audio", "video", "document", "location", name="messagetype", create_type=False),
                nullable=False,
                server_default="text",
            ),
            sa.Column("raw_content", sa.Text, nullable=True),
            sa.Column("media_url", sa.Text, nullable=True),
            sa.Column("media_mime_type", sa.String(100), nullable=True),
            sa.Column(
                "source",
                postgresql.ENUM("whatsapp_group", "manual_chat", name="messagesource", create_type=False),
                nullable=False,
                server_default="whatsapp_group",
            ),
            sa.Column("language", sa.String(10), nullable=False, server_default="en"),
            sa.Column("processed", sa.Boolean, nullable=False, server_default="false"),
            sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("whatsapp_timestamp", sa.Integer, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
    _create_index_if_not_exists(conn, "unique_whatsapp_message_id", "whatsapp_messages", ["whatsapp_message_id"], unique=True)
    _create_index_if_not_exists(conn, "idx_whatsapp_messages_group", "whatsapp_messages", ["group_id"])
    _create_index_if_not_exists(conn, "idx_whatsapp_messages_processed", "whatsapp_messages", ["processed"])

    # events
    if not _table_exists(conn, "events"):
        op.create_table(
            "events",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("whatsapp_message_id", sa.String(100), sa.ForeignKey("whatsapp_messages.whatsapp_message_id", ondelete="CASCADE"), nullable=False),
            sa.Column("group_id", sa.String(100), sa.ForeignKey("whatsapp_groups.group_id", ondelete="SET NULL"), nullable=True),
            sa.Column(
                "event_type",
                postgresql.ENUM(
                    "maintenance_request", "lease_inquiry", "payment_issue",
                    "move_in", "move_out", "noise_complaint", "safety_concern",
                    "amenity_request", "general_inquiry", "other",
                    name="eventtype", create_type=False,
                ),
                nullable=False,
            ),
            sa.Column(
                "priority",
                postgresql.ENUM("low", "medium", "high", "urgent", name="priority", create_type=False),
                nullable=False,
                server_default="medium",
            ),
            sa.Column(
                "status",
                postgresql.ENUM("open", "in_progress", "resolved", "closed", name="eventstatus", create_type=False),
                nullable=False,
                server_default="open",
            ),
            sa.Column("title", sa.String(500), nullable=False),
            sa.Column("description", sa.Text, nullable=False),
            sa.Column("tenant_id", sa.String(100), nullable=True),
            sa.Column("tenant_name", sa.String(255), nullable=True),
            sa.Column("property_id", sa.String(100), nullable=True),
            sa.Column("community_id", sa.String(100), nullable=True),
            sa.Column("address", sa.Text, nullable=True),
            sa.Column("ai_confidence", sa.Float, nullable=True),
            sa.Column("raw_ai_response", postgresql.JSONB, nullable=True),
            sa.Column(
                "source",
                postgresql.ENUM("whatsapp_group", "manual_chat", name="eventsource", create_type=False),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
    _create_index_if_not_exists(conn, "uq_events_whatsapp_message_id", "events", ["whatsapp_message_id"], unique=True)
    _create_index_if_not_exists(conn, "idx_events_group_id", "events", ["group_id"])
    _create_index_if_not_exists(conn, "idx_events_status", "events", ["status"])
    _create_index_if_not_exists(conn, "idx_events_event_type", "events", ["event_type"])
    _create_index_if_not_exists(conn, "idx_events_priority", "events", ["priority"])
    _create_index_if_not_exists(conn, "idx_events_created_at", "events", ["created_at"])


def downgrade() -> None:
    op.drop_table("events")
    op.drop_table("whatsapp_messages")
    op.drop_table("whatsapp_groups")
    op.execute("DROP TYPE IF EXISTS eventtype")
    op.execute("DROP TYPE IF EXISTS priority")
    op.execute("DROP TYPE IF EXISTS eventstatus")
    op.execute("DROP TYPE IF EXISTS eventsource")
    op.execute("DROP TYPE IF EXISTS messagetype")
    op.execute("DROP TYPE IF EXISTS messagesource")
