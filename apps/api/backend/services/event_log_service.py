import json
from typing import Any
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine
from backend.schemas.event_log import EventLogCreateRequest


ALLOWED_EVENT_TYPES = {"user_behavior", "domain_event", "system_event"}
ALLOWED_SOURCES = {"frontend", "backend", "script"}


def record_event(
    event_name: str,
    event_type: str,
    source: str,
    *,
    user_id: UUID | None = None,
    session_id: UUID | None = None,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if event_type not in ALLOWED_EVENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported event type",
        )

    if source not in ALLOWED_SOURCES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported event source",
        )

    event_id = uuid4()
    normalized_properties = properties or {}

    insert_query = text("""
        INSERT INTO event_logs (
            event_id,
            event_name,
            event_type,
            user_id,
            session_id,
            entity_type,
            entity_id,
            occurred_at,
            source,
            properties,
            created_at
        )
        VALUES (
            :event_id,
            :event_name,
            :event_type,
            :user_id,
            :session_id,
            :entity_type,
            :entity_id,
            CURRENT_TIMESTAMP,
            :source,
            CAST(:properties AS JSONB),
            CURRENT_TIMESTAMP
        )
        RETURNING
            event_id,
            event_name,
            event_type,
            user_id,
            session_id,
            entity_type,
            entity_id,
            occurred_at,
            source,
            properties,
            created_at
    """)

    with engine.begin() as connection:
        event = connection.execute(
            insert_query,
            {
                "event_id": event_id,
                "event_name": event_name,
                "event_type": event_type,
                "user_id": user_id,
                "session_id": session_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "source": source,
                "properties": json.dumps(normalized_properties, default=str),
            },
        ).mappings().first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record event log",
        )

    return {
        **dict(event),
        "message": "Event log recorded successfully",
    }


def create_event_log(payload: EventLogCreateRequest) -> dict[str, Any]:
    return record_event(
        event_name=payload.event_name,
        event_type=payload.event_type,
        source=payload.source,
        user_id=payload.user_id,
        session_id=payload.session_id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        properties=payload.properties,
    )