import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, DateTime, Enum as SAEnum, Index, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


def utcnow():
    return datetime.now(timezone.utc)


class EventType(str, enum.Enum):
    maintenance_request = "maintenance_request"
    lease_inquiry = "lease_inquiry"
    payment_issue = "payment_issue"
    move_in = "move_in"
    move_out = "move_out"
    noise_complaint = "noise_complaint"
    safety_concern = "safety_concern"
    amenity_request = "amenity_request"
    general_inquiry = "general_inquiry"
    other = "other"


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class EventStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class EventSource(str, enum.Enum):
    whatsapp_group = "whatsapp_group"
    manual_chat = "manual_chat"
    file_upload = "file_upload"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    whatsapp_message_id: Mapped[str | None] = mapped_column(
        String(100),
        ForeignKey("whatsapp_messages.whatsapp_message_id", ondelete="CASCADE"),
        unique=True,
        nullable=True,
    )
    group_id: Mapped[str | None] = mapped_column(
        String(100),
        ForeignKey("whatsapp_groups.group_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[EventType] = mapped_column(SAEnum(EventType), nullable=False, index=True)
    priority: Mapped[Priority] = mapped_column(
        SAEnum(Priority), default=Priority.medium, nullable=False, index=True
    )
    status: Mapped[EventStatus] = mapped_column(
        SAEnum(EventStatus), default=EventStatus.open, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tenant_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tenant_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    property_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    community_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_ai_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source: Mapped[EventSource] = mapped_column(SAEnum(EventSource), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    message: Mapped["WhatsappMessage | None"] = relationship(
        "WhatsappMessage", back_populates="event"
    )
    group: Mapped["WhatsappGroup | None"] = relationship(
        "WhatsappGroup", back_populates="events", foreign_keys=[group_id]
    )

    __table_args__ = (
        Index("idx_events_group_id", "group_id"),
        Index("idx_events_status", "status"),
        Index("idx_events_event_type", "event_type"),
        Index("idx_events_priority", "priority"),
        Index("idx_events_created_at", "created_at"),
    )
