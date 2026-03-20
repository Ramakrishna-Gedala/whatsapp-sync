import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, DateTime, Integer, Enum as SAEnum, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


def utcnow():
    return datetime.now(timezone.utc)


class MessageType(str, enum.Enum):
    text = "text"
    image = "image"
    audio = "audio"
    video = "video"
    document = "document"
    location = "location"


class MessageSource(str, enum.Enum):
    whatsapp_group = "whatsapp_group"
    manual_chat = "manual_chat"
    file_upload = "file_upload"


class WhatsappMessage(Base):
    __tablename__ = "whatsapp_messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    whatsapp_message_id: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )
    group_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("whatsapp_groups.group_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sender_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sender_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message_type: Mapped[MessageType] = mapped_column(
        SAEnum(MessageType), default=MessageType.text, nullable=False
    )
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[MessageSource] = mapped_column(
        SAEnum(MessageSource), default=MessageSource.whatsapp_group, nullable=False
    )
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    whatsapp_timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    group: Mapped["WhatsappGroup | None"] = relationship(
        "WhatsappGroup", back_populates="messages", foreign_keys=[group_id]
    )
    event: Mapped["Event | None"] = relationship(
        "Event", back_populates="message", uselist=False
    )

    __table_args__ = (
        Index("idx_whatsapp_messages_group", "group_id"),
        Index("idx_whatsapp_messages_processed", "processed"),
    )
