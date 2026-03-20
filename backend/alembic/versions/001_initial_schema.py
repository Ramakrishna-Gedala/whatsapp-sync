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


def upgrade() -> None:
    # whatsapp_groups
    op.create_table(
        "whatsapp_groups",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("group_id", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("uq_whatsapp_groups_group_id", "whatsapp_groups", ["group_id"], unique=True)

    # whatsapp_messages
    op.create_table(
        "whatsapp_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("whatsapp_message_id", sa.String(100), nullable=False),
        sa.Column("group_id", sa.String(100), sa.ForeignKey("whatsapp_groups.group_id", ondelete="SET NULL"), nullable=True),
        sa.Column("sender_id", sa.String(100), nullable=False),
        sa.Column("sender_name", sa.String(255), nullable=True),
        sa.Column(
            "message_type",
            sa.Enum("text", "image", "audio", "video", "document", "location", name="messagetype"),
            nullable=False,
            server_default="text",
        ),
        sa.Column("raw_content", sa.Text, nullable=True),
        sa.Column("media_url", sa.Text, nullable=True),
        sa.Column("media_mime_type", sa.String(100), nullable=True),
        sa.Column(
            "source",
            sa.Enum("whatsapp_group", "manual_chat", name="messagesource"),
            nullable=False,
            server_default="whatsapp_group",
        ),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("processed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("whatsapp_timestamp", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("unique_whatsapp_message_id", "whatsapp_messages", ["whatsapp_message_id"], unique=True)
    op.create_index("idx_whatsapp_messages_group", "whatsapp_messages", ["group_id"])
    op.create_index("idx_whatsapp_messages_processed", "whatsapp_messages", ["processed"])

    # events
    op.create_table(
        "events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("whatsapp_message_id", sa.String(100), sa.ForeignKey("whatsapp_messages.whatsapp_message_id", ondelete="CASCADE"), nullable=False),
        sa.Column("group_id", sa.String(100), sa.ForeignKey("whatsapp_groups.group_id", ondelete="SET NULL"), nullable=True),
        sa.Column(
            "event_type",
            sa.Enum(
                "maintenance_request", "lease_inquiry", "payment_issue",
                "move_in", "move_out", "noise_complaint", "safety_concern",
                "amenity_request", "general_inquiry", "other",
                name="eventtype",
            ),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.Enum("low", "medium", "high", "urgent", name="priority"),
            nullable=False,
            server_default="medium",
        ),
        sa.Column(
            "status",
            sa.Enum("open", "in_progress", "resolved", "closed", name="eventstatus"),
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
            sa.Enum("whatsapp_group", "manual_chat", name="eventsource"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("uq_events_whatsapp_message_id", "events", ["whatsapp_message_id"], unique=True)
    op.create_index("idx_events_group_id", "events", ["group_id"])
    op.create_index("idx_events_status", "events", ["status"])
    op.create_index("idx_events_event_type", "events", ["event_type"])
    op.create_index("idx_events_priority", "events", ["priority"])
    op.create_index("idx_events_created_at", "events", ["created_at"])


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
