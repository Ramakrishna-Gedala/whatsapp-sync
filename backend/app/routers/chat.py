import uuid
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.event_service import event_service
from app.schemas.message import ChatMessageRequest
from app.schemas.event import EventOut
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message")
async def process_chat_message(
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Parse a manually entered message and create an event.
    Uses a synthetic whatsapp_message_id for deduplication tracking.
    """
    if not request.text.strip():
        raise HTTPException(status_code=422, detail="Message text cannot be empty")

    if len(request.text) > 2000:
        raise HTTPException(status_code=422, detail="Message too long (max 2000 chars)")

    # Generate synthetic ID for dedup tracking
    synthetic_id = f"manual_{uuid.uuid4()}"

    raw_message = {
        "idMessage": synthetic_id,
        "textMessage": request.text,
        "typeMessage": "textMessage",
        "senderId": "manual@user.com",
        "senderName": "Manual Input",
        "timestamp": int(time.time()),
        "source": "manual_chat",
    }

    logger.info(f"Processing manual chat message (id={synthetic_id})")

    event = await event_service.process_and_save(
        db=db,
        raw_message=raw_message,
        source="manual_chat",
        group_id=None,
    )

    if not event:
        raise HTTPException(status_code=409, detail="Message already processed")

    event_out = EventOut.model_validate(event)

    formatted = (
        f"✅ Event Created: {event_out.event_type.value.replace('_', ' ').title()}\n"
        f"Priority: {event_out.priority.value.upper()}\n"
        f"Title: {event_out.title}\n"
        + (f"Tenant: {event_out.tenant_name}\n" if event_out.tenant_name else "")
        + (f"Unit: {event_out.property_id}\n" if event_out.property_id else "")
        + (f"Community: {event_out.community_id}\n" if event_out.community_id else "")
    )

    return {
        "event": event_out.model_dump(),
        "formatted_message": formatted,
    }
