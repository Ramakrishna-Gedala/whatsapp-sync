"""
Orchestrates: file bytes → parse → OpenAI → events in DB.
"""
import asyncio
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.services.file_parsers.factory import FileParserFactory
from app.services.file_parsers.base import ParsedMessage
from app.services.event_service import event_service
from app.models.event import Event
from app.models.group import WhatsappGroup
from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_CONCURRENT = 5


@dataclass
class FileUploadResult:
    file_name: str
    total_messages_found: int
    events_created: int
    events_failed: int
    events: list[Event]
    parse_errors: list[str] = field(default_factory=list)


class FileUploadService:

    async def process_file(
        self,
        db: AsyncSession,
        file_bytes: bytes,
        file_name: str,
        mime_type: str,
        group_id: str | None = None,
    ) -> FileUploadResult:
        """
        Full pipeline: file bytes → parse → OpenAI → events in DB.
        whatsapp_message_id is NULL for all file-uploaded messages
        (exported files carry no Green API message IDs).
        """
        # 1. Select parser
        parser = FileParserFactory.get_parser(mime_type)
        if not parser:
            raise ValueError(
                f"Unsupported file type: '{mime_type}'. "
                f"Supported: {FileParserFactory.supported_types()}"
            )

        # 2. Validate size
        if len(file_bytes) > parser.max_file_size_bytes:
            max_mb = parser.max_file_size_bytes / (1024 * 1024)
            raise ValueError(f"File too large. Maximum: {max_mb:.0f} MB")

        # 3. Parse
        parse_result = await parser.parse(file_bytes, file_name)
        logger.info(
            f"Parsed '{file_name}': {parse_result.total_found} messages found, "
            f"{len(parse_result.parse_errors)} parse errors"
        )

        if not parse_result.messages:
            return FileUploadResult(
                file_name=file_name,
                total_messages_found=0,
                events_created=0,
                events_failed=0,
                events=[],
                parse_errors=parse_result.parse_errors or ["No valid messages found in file"],
            )

        # 4. Ensure group exists in whatsapp_groups (FK constraint)
        if group_id:
            from app.database import AsyncSessionLocal
            async with AsyncSessionLocal() as gdb:
                stmt = pg_insert(WhatsappGroup).values(
                    id=group_id,
                    group_id=group_id,
                    name=group_id,
                ).on_conflict_do_nothing(index_elements=["group_id"])
                await gdb.execute(stmt)
                await gdb.commit()

        # 5. Process each message in parallel (own session per task)
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        created: list[Event] = []
        failed = 0

        async def process_one(msg: ParsedMessage) -> Event | None:
            async with semaphore:
                # Prefix sender name so OpenAI has more context
                enriched = (
                    f"[From: {msg.sender_name}] {msg.content}"
                    if msg.sender_name else msg.content
                )
                raw_message = {
                    "idMessage": None,          # NULL → skip dedup, no Green API ID
                    "senderId": None,
                    "senderName": msg.sender_name,
                    "typeMessage": "textMessage",
                    "textMessage": enriched,
                    "timestamp": 0,
                }
                from app.database import AsyncSessionLocal
                async with AsyncSessionLocal() as own_db:
                    return await event_service.process_and_save(
                        db=own_db,
                        raw_message=raw_message,
                        source="file_upload",
                        group_id=group_id,
                    )

        results = await asyncio.gather(
            *[process_one(m) for m in parse_result.messages],
            return_exceptions=True,
        )

        for r in results:
            if isinstance(r, Exception):
                logger.error(f"File upload message processing error: {r}")
                failed += 1
            elif r is None:
                failed += 1
            else:
                created.append(r)

        created.sort(key=lambda e: e.created_at, reverse=True)

        logger.info(
            f"File upload complete: {len(created)} events created, {failed} failed"
        )
        return FileUploadResult(
            file_name=file_name,
            total_messages_found=parse_result.total_found,
            events_created=len(created),
            events_failed=failed,
            events=created,
            parse_errors=parse_result.parse_errors,
        )


file_upload_service = FileUploadService()
