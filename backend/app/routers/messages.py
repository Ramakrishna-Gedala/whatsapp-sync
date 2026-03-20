import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.greenapi import green_api_service
from app.services.message_processor import process_messages_batch
from app.schemas.message import ProcessMessagesRequest, ProcessMessagesResponse
from app.schemas.event import EventOut
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/groups", tags=["messages"])


@router.post("/{group_id}/messages/process")
async def process_group_messages(
    group_id: str,
    request: ProcessMessagesRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch recent messages from a WhatsApp group and process them into events.
    Duplicate messages (by whatsapp_message_id) are silently skipped.
    """
    logger.info(f"Processing messages for group {group_id}, limit={request.limit}")

    # Fetch group name for FK upsert, and messages concurrently
    groups, messages = await asyncio.gather(
        green_api_service.get_groups(),
        green_api_service.get_chat_history(group_id, count=request.limit),
    )
    group_name = next((g["name"] for g in groups if g["id"] == group_id), group_id)

    if not messages:
        return {
            "events_created": 0,
            "events_skipped": 0,
            "events": [],
        }

    # Process in parallel — each message gets its own DB session
    created_events, skipped = await process_messages_batch(
        db=db,
        messages=messages,
        source="whatsapp_group",
        group_id=group_id,
        group_name=group_name,
    )

    # Sort by created_at DESC
    created_events.sort(key=lambda e: e.created_at, reverse=True)

    return {
        "events_created": len(created_events),
        "events_skipped": skipped,
        "events": [EventOut.model_validate(e).model_dump() for e in created_events],
    }
