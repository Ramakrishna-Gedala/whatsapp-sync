from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.event import Event, EventType, Priority, EventStatus, EventSource
from app.models.message import WhatsappMessage, MessageType, MessageSource
from app.schemas.event import EventFilters
from app.services.openai_service import openai_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


def utcnow():
    return datetime.now(timezone.utc)


class EventService:
    async def process_and_save(
        self,
        db: AsyncSession,
        raw_message: dict,
        source: str,
        group_id: str | None = None,
    ) -> Event | None:
        """
        Process a raw message dict and save as Event.
        Returns None if message was already processed (deduplication).
        """
        whatsapp_message_id: str | None = (
            raw_message.get("idMessage") or raw_message.get("whatsapp_message_id") or None
        )

        # Step 1: Deduplication — only for messages that have a real ID.
        # File-uploaded messages have idMessage=None → always process (no dedup possible).
        if whatsapp_message_id is not None:
            existing = await db.execute(
                select(WhatsappMessage).where(
                    WhatsappMessage.whatsapp_message_id == whatsapp_message_id
                )
            )
            if existing.scalar_one_or_none() is not None:
                logger.debug(f"Skipping duplicate message: {whatsapp_message_id}")
                return None

        # Step 2: Extract raw content
        raw_content = (
            raw_message.get("textMessage")
            or raw_message.get("caption")
            or raw_message.get("raw_content")
            or ""
        )
        sender_id = raw_message.get("senderId") or raw_message.get("sender_id", "unknown@c.us")
        sender_name = raw_message.get("senderName") or raw_message.get("sender_name")
        whatsapp_timestamp = raw_message.get("timestamp") or raw_message.get("whatsapp_timestamp", 0)

        # Normalize message type
        msg_type_str = raw_message.get("typeMessage", "textMessage")
        msg_type_map = {
            "textMessage": MessageType.text,
            "imageMessage": MessageType.image,
            "audioMessage": MessageType.audio,
            "videoMessage": MessageType.video,
            "documentMessage": MessageType.document,
            "locationMessage": MessageType.location,
        }
        msg_type = msg_type_map.get(msg_type_str, MessageType.text)

        source_map = {
            "whatsapp_group": MessageSource.whatsapp_group,
            "manual_chat": MessageSource.manual_chat,
            "file_upload": MessageSource.file_upload,
        }
        source_enum = source_map.get(source, MessageSource.manual_chat)

        # Step 3: Save raw message
        db_message = WhatsappMessage(
            whatsapp_message_id=whatsapp_message_id,
            group_id=group_id,
            sender_id=sender_id,
            sender_name=sender_name,
            message_type=msg_type,
            raw_content=raw_content,
            source=source_enum,
            processed=False,
            whatsapp_timestamp=int(whatsapp_timestamp) if whatsapp_timestamp else 0,
        )
        db.add(db_message)
        await db.flush()  # get id without committing

        try:
            # Step 4: Parse with OpenAI
            parsed = await openai_service.parse_message(raw_content, source=source)

            event_source_map = {
                "whatsapp_group": EventSource.whatsapp_group,
                "manual_chat": EventSource.manual_chat,
                "file_upload": EventSource.file_upload,
            }
            event_source = event_source_map.get(source, EventSource.manual_chat)

            # Step 5: Create Event
            event = Event(
                whatsapp_message_id=whatsapp_message_id,
                group_id=group_id,
                event_type=EventType(parsed["event_type"]),
                priority=Priority(parsed["priority"]),
                status=EventStatus.open,
                title=parsed["title"],
                description=parsed["description"],
                tenant_id=parsed.get("tenant_id"),
                tenant_name=parsed.get("tenant_name"),
                property_id=parsed.get("property_id"),
                community_id=parsed.get("community_id"),
                address=parsed.get("address"),
                ai_confidence=parsed.get("confidence"),
                raw_ai_response=parsed.get("raw_response"),
                source=event_source,
            )
            db.add(event)

            # Step 6: Mark message as processed
            db_message.processed = True
            db_message.processed_at = utcnow()

            await db.commit()
            await db.refresh(event)
            logger.info(f"Created event {event.id} from message {whatsapp_message_id}")
            return event

        except Exception as e:
            await db.rollback()
            logger.error(f"Error processing message {whatsapp_message_id}: {e}")
            raise

    async def get_events(
        self, db: AsyncSession, filters: EventFilters
    ) -> tuple[list[Event], int]:
        """Get paginated events with filters."""
        query = select(Event)
        count_query = select(func.count(Event.id))

        if filters.group_id:
            query = query.where(Event.group_id == filters.group_id)
            count_query = count_query.where(Event.group_id == filters.group_id)
        if filters.event_type:
            query = query.where(Event.event_type == filters.event_type)
            count_query = count_query.where(Event.event_type == filters.event_type)
        if filters.priority:
            query = query.where(Event.priority == filters.priority)
            count_query = count_query.where(Event.priority == filters.priority)
        if filters.status:
            query = query.where(Event.status == filters.status)
            count_query = count_query.where(Event.status == filters.status)

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Event.created_at.desc()).offset(filters.skip).limit(filters.limit)
        result = await db.execute(query)
        events = list(result.scalars().all())

        return events, total

    async def update_status(
        self, db: AsyncSession, event_id: str, status: EventStatus
    ) -> Event | None:
        result = await db.execute(select(Event).where(Event.id == event_id))
        event = result.scalar_one_or_none()
        if not event:
            return None
        event.status = status
        event.updated_at = utcnow()
        await db.commit()
        await db.refresh(event)
        return event


event_service = EventService()
