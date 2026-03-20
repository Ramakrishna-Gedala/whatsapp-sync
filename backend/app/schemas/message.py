from pydantic import BaseModel
from datetime import datetime
from app.models.message import MessageType, MessageSource


class MessageOut(BaseModel):
    id: str
    whatsapp_message_id: str
    group_id: str | None
    sender_id: str
    sender_name: str | None
    message_type: MessageType
    raw_content: str | None
    source: MessageSource
    processed: bool
    whatsapp_timestamp: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProcessMessagesRequest(BaseModel):
    limit: int = 20


class ProcessMessagesResponse(BaseModel):
    events_created: int
    events_skipped: int
    events: list


class ChatMessageRequest(BaseModel):
    text: str
    message_type: str = "text"


class ChatMessageResponse(BaseModel):
    event: dict
    formatted_message: str
