from uuid import UUID

from fastapi import APIRouter, status

from backend.schemas.session import (
    SessionEndResponse,
    SessionResponse,
    SessionStartRequest,
)
from backend.services.session_service import create_session, end_session

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def start_session(payload: SessionStartRequest) -> SessionResponse:
    session = create_session(payload)
    return SessionResponse(**session)


@router.patch("/{session_id}/end", response_model=SessionEndResponse, status_code=status.HTTP_200_OK)
def finish_session(session_id: UUID) -> SessionEndResponse:
    result = end_session(session_id)
    return SessionEndResponse(**result)