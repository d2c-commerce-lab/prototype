from fastapi import APIRouter, status

from backend.schemas.event_log import (
    EventLogCreateRequest,
    EventLogCreateResponse,
)
from backend.services.event_log_service import create_event_log

router = APIRouter(prefix="/events", tags=["events"])


@router.post(
    "",
    response_model=EventLogCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(payload: EventLogCreateRequest) -> EventLogCreateResponse:
    result = create_event_log(payload)
    return EventLogCreateResponse(**result)