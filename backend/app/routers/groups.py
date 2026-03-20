import time
from fastapi import APIRouter, HTTPException
from app.services.greenapi import green_api_service
from app.schemas.group import GroupsResponse, GreenAPIGroup
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/groups", tags=["groups"])

# Simple in-memory TTL cache
_groups_cache: dict = {"data": None, "expires_at": 0}
CACHE_TTL = 60  # seconds


@router.get("", response_model=GroupsResponse)
async def list_groups():
    """Fetch all WhatsApp groups via Green API (cached 60s)."""
    now = time.time()

    if _groups_cache["data"] is not None and now < _groups_cache["expires_at"]:
        logger.debug("Returning cached groups")
        groups = _groups_cache["data"]
    else:
        raw_groups = await green_api_service.get_groups()
        groups = [
            GreenAPIGroup(
                id=g["id"],
                name=g["name"],
                description=g.get("description"),
            )
            for g in raw_groups
        ]
        _groups_cache["data"] = groups
        _groups_cache["expires_at"] = now + CACHE_TTL
        logger.info(f"Fetched and cached {len(groups)} groups")

    return GroupsResponse(
        groups=[
            {
                "id": str(i),
                "group_id": g.id,
                "name": g.name,
                "description": g.description,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
            for i, g in enumerate(groups)
        ],
        total=len(groups),
    )


@router.get("/{group_id}")
async def get_group(group_id: str):
    """Get a specific group by ID."""
    raw_groups = await green_api_service.get_groups()
    for g in raw_groups:
        if g["id"] == group_id:
            return {"id": group_id, "name": g["name"], "description": g.get("description")}
    raise HTTPException(status_code=404, detail=f"Group {group_id} not found")
