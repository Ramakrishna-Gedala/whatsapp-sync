from pydantic import BaseModel
from datetime import datetime
from app.models.event import EventType, Priority, EventStatus, EventSource


class EventOut(BaseModel):
    id: str
    whatsapp_message_id: str | None
    group_id: str | None
    event_type: EventType
    priority: Priority
    status: EventStatus
    title: str
    description: str
    tenant_id: str | None
    tenant_name: str | None
    property_id: str | None
    community_id: str | None
    address: str | None
    ai_confidence: float | None
    source: EventSource
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventsResponse(BaseModel):
    events: list[EventOut]
    total: int


class EventStatusUpdate(BaseModel):
    status: EventStatus


class EventFilters(BaseModel):
    group_id: str | None = None
    event_type: EventType | None = None
    priority: Priority | None = None
    status: EventStatus | None = None
    skip: int = 0
    limit: int = 50


class ParsedEventData(BaseModel):
    event_type: EventType
    priority: Priority
    title: str
    description: str
    tenant_id: str | None = None
    tenant_name: str | None = None
    property_id: str | None = None
    community_id: str | None = None
    address: str | None = None
    confidence: float = 0.5
