"""
Message processor utility for batch processing with concurrency control.
"""
import asyncio
from sqlalchemy import select, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.database import AsyncSessionLocal
from app.models.group import WhatsappGroup
from app.services.event_service import event_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_CONCURRENT_OPENAI_CALLS = 5


async def _ensure_group_exists(group_id: str, group_name: str = "") -> None:
    """Upsert the group into whatsapp_groups so FK constraints are satisfied."""
    async with AsyncSessionLocal() as db:
        stmt = pg_insert(WhatsappGroup).values(
            id=group_id,  # use group_id as PK shortcut
            group_id=group_id,
            name=group_name or group_id,
        ).on_conflict_do_nothing(index_elements=["group_id"])
        await db.execute(stmt)
        await db.commit()


async def process_messages_batch(
    db,  # kept for API compatibility but NOT used for concurrent tasks
    messages: list[dict],
    source: str,
    group_id: str | None = None,
    group_name: str = "",
) -> tuple[list, int]:
    """
    Process a batch of raw messages in parallel.
    Each message gets its own DB session to avoid asyncpg concurrent-operation errors.

    Returns: (created_events, skipped_count)
    """
    # Ensure the group row exists before any message FK references it
    if group_id:
        await _ensure_group_exists(group_id, group_name)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_OPENAI_CALLS)
    created_events = []
    skipped = 0

    async def process_one(raw_msg: dict):
        async with semaphore:
            # Each task gets its own isolated session
            async with AsyncSessionLocal() as own_db:
                return await event_service.process_and_save(
                    db=own_db,
                    raw_message=raw_msg,
                    source=source,
                    group_id=group_id,
                )

    # Filter to text messages only (future: extend to other types)
    processable = [
        m for m in messages
        if m.get("typeMessage") in ("textMessage", None)
        and (m.get("textMessage") or m.get("raw_content"))
    ]

    if not processable:
        logger.info("No processable text messages found in batch")
        return [], len(messages)

    results = await asyncio.gather(
        *[process_one(m) for m in processable],
        return_exceptions=True,
    )

    for r in results:
        if isinstance(r, Exception):
            logger.error(f"Error processing message: {r}")
        elif r is None:
            skipped += 1
        else:
            created_events.append(r)

    skipped += len(messages) - len(processable)
    logger.info(f"Batch complete: {len(created_events)} created, {skipped} skipped")
    return created_events, skipped
