from pydantic import BaseModel
from datetime import datetime


class GroupBase(BaseModel):
    group_id: str
    name: str
    description: str | None = None


class GroupOut(GroupBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GroupsResponse(BaseModel):
    groups: list[GroupOut]
    total: int


class GreenAPIGroup(BaseModel):
    id: str
    name: str
    description: str | None = None
