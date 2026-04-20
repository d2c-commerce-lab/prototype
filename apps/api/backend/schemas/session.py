from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SessionStartRequest(BaseModel):
    user_id: UUID | None = None
    campaign_id: UUID | None = None
    anonymous_id: str = Field(min_length=1, max_length=255)
    platform: str = Field(min_length=1, max_length=50)
    device_type: str = Field(min_length=1, max_length=50)
    os_type: str | None = Field(default=None, max_length=50)
    browser_type: str | None = Field(default=None, max_length=50)
    traffic_source: str | None = Field(default=None, max_length=100)
    traffic_medium: str | None = Field(default=None, max_length=100)
    landing_page_url: str | None = None
    referrer_url: str | None = None


class SessionResponse(BaseModel):
    session_id: UUID
    user_id: UUID | None = None
    campaign_id: UUID | None = None
    anonymous_id: str
    session_start_at: datetime
    session_end_at: datetime | None = None
    platform: str
    device_type: str
    os_type: str | None = None
    browser_type: str | None = None
    traffic_source: str | None = None
    traffic_medium: str | None = None
    landing_page_url: str | None = None
    referrer_url: str | None = None


class SessionEndResponse(BaseModel):
    session_id: UUID
    session_end_at: datetime
    message: str