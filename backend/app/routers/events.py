from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.event_service import event_service
from app.models.event import EventType, Priority, EventStatus
from app.schemas.event import EventOut, EventsResponse, EventFilters, EventStatusUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=EventsResponse)
async def list_events(
    group_id: str | None = Query(None),
    event_type: EventType | None = Query(None),
    priority: Priority | None = Query(None),
    status: EventStatus | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List events with optional filters, ordered by created_at DESC."""
    filters = EventFilters(
        group_id=group_id,
        event_type=event_type,
        priority=priority,
        status=status,
        skip=skip,
        limit=limit,
    )
    events, total = await event_service.get_events(db, filters)
    return EventsResponse(
        events=[EventOut.model_validate(e) for e in events],
        total=total,
    )


@router.get("/{event_id}", response_model=EventOut)
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single event by ID."""
    from sqlalchemy import select
    from app.models.event import Event

    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return EventOut.model_validate(event)


@router.patch("/{event_id}/status", response_model=EventOut)
async def update_event_status(
    event_id: str,
    body: EventStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update the status of an event."""
    event = await event_service.update_status(db, event_id, body.status)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return EventOut.model_validate(event)
