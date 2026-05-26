from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class EventLogCreateRequest(BaseModel):
    event_name: str = Field(..., min_length=1, max_length=100)
    event_type: str = Field(..., min_length=1, max_length=50)
    user_id: UUID | None = None
    session_id: UUID | None = None
    entity_type: str | None = Field(default=None, max_length=50)
    entity_id: UUID | None = None
    source: str = Field(..., min_length=1, max_length=50)
    properties: dict[str, Any] = Field(default_factory=dict)


class EventLogCreateResponse(BaseModel):
    event_id: UUID
    event_name: str
    event_type: str
    user_id: UUID | None = None
    session_id: UUID | None = None
    entity_type: str | None = None
    entity_id: UUID | None = None
    occurred_at: datetime
    source: str
    properties: dict[str, Any]
    created_at: datetime
    message: str