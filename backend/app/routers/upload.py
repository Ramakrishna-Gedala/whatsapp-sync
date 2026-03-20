from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.file_upload_service import file_upload_service
from app.services.file_parsers.factory import FileParserFactory
from app.schemas.event import EventOut
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    group_id: str | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a WhatsApp chat export file (.txt) and create events from each message.
    whatsapp_message_id is stored as NULL for file-sourced messages.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    contents = await file.read()

    # Resolve MIME type — browsers sometimes send 'application/octet-stream' for .txt
    mime_type = file.content_type or "text/plain"
    if file.filename.lower().endswith(".txt") and mime_type in (
        "application/octet-stream", "binary/octet-stream", ""
    ):
        mime_type = "text/plain"

    logger.info(
        f"File upload: '{file.filename}', size={len(contents)} bytes, "
        f"mime={mime_type}, group_id={group_id}"
    )

    try:
        result = await file_upload_service.process_file(
            db=db,
            file_bytes=contents,
            file_name=file.filename,
            mime_type=mime_type,
            group_id=group_id if group_id else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"File upload processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

    return {
        "file_name": result.file_name,
        "total_messages_found": result.total_messages_found,
        "events_created": result.events_created,
        "events_failed": result.events_failed,
        "events": [EventOut.model_validate(e).model_dump() for e in result.events],
        "parse_errors": result.parse_errors,
    }


@router.get("/supported-types")
def get_supported_types():
    """Returns the list of currently supported upload MIME types."""
    return {"supported_mime_types": FileParserFactory.supported_types()}
