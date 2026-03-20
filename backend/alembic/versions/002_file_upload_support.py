"""Add file_upload source, nullable whatsapp_message_id, nullable sender_id

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

Changes:
  1. messagesource enum: add 'file_upload'
  2. eventsource enum:   add 'file_upload'
  3. whatsapp_messages.whatsapp_message_id: NOT NULL → NULL
  4. whatsapp_messages.sender_id:           NOT NULL → NULL
  5. events.whatsapp_message_id:            NOT NULL → NULL
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ALTER TYPE ... ADD VALUE must run outside a transaction block in PostgreSQL
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE messagesource ADD VALUE IF NOT EXISTS 'file_upload'")
        op.execute("ALTER TYPE eventsource ADD VALUE IF NOT EXISTS 'file_upload'")

    # Make whatsapp_message_id nullable in whatsapp_messages
    op.alter_column(
        "whatsapp_messages",
        "whatsapp_message_id",
        existing_type=sa.String(100),
        nullable=True,
    )

    # Make sender_id nullable in whatsapp_messages (file uploads have no sender ID)
    op.alter_column(
        "whatsapp_messages",
        "sender_id",
        existing_type=sa.String(100),
        nullable=True,
    )

    # Make whatsapp_message_id nullable in events
    op.alter_column(
        "events",
        "whatsapp_message_id",
        existing_type=sa.String(100),
        nullable=True,
    )


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values.
    # To fully downgrade, recreate the enum types without 'file_upload'.
    # For simplicity we only reverse the nullable changes here.

    op.alter_column(
        "events",
        "whatsapp_message_id",
        existing_type=sa.String(100),
        nullable=False,
    )
    op.alter_column(
        "whatsapp_messages",
        "sender_id",
        existing_type=sa.String(100),
        nullable=False,
    )
    op.alter_column(
        "whatsapp_messages",
        "whatsapp_message_id",
        existing_type=sa.String(100),
        nullable=False,
    )
