from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine
from backend.schemas.session import SessionStartRequest


def create_session(payload: SessionStartRequest) -> dict[str, Any]:
    query = text("""
        INSERT INTO sessions (
            user_id,
            campaign_id,
            anonymous_id,
            session_start_at,
            platform,
            device_type,
            os_type,
            browser_type,
            traffic_source,
            traffic_medium,
            landing_page_url,
            referrer_url,
            created_at
        )
        VALUES (
            :user_id,
            :campaign_id,
            :anonymous_id,
            CURRENT_TIMESTAMP,
            :platform,
            :device_type,
            :os_type,
            :browser_type,
            :traffic_source,
            :traffic_medium,
            :landing_page_url,
            :referrer_url,
            CURRENT_TIMESTAMP
        )
        RETURNING
            session_id,
            user_id,
            campaign_id,
            anonymous_id,
            session_start_at,
            session_end_at,
            platform,
            device_type,
            os_type,
            browser_type,
            traffic_source,
            traffic_medium,
            landing_page_url,
            referrer_url
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "user_id": payload.user_id,
                "campaign_id": payload.campaign_id,
                "anonymous_id": payload.anonymous_id,
                "platform": payload.platform,
                "device_type": payload.device_type,
                "os_type": payload.os_type,
                "browser_type": payload.browser_type,
                "traffic_source": payload.traffic_source,
                "traffic_medium": payload.traffic_medium,
                "landing_page_url": payload.landing_page_url,
                "referrer_url": payload.referrer_url,
            },
        ).mappings().first()

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session",
        )

    return dict(result)


def end_session(session_id: UUID) -> dict[str, Any]:
    query = text("""
        UPDATE sessions
        SET
            session_end_at = CURRENT_TIMESTAMP
        WHERE session_id = :session_id
          AND session_end_at IS NULL
        RETURNING
            session_id,
            session_end_at
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {"session_id": session_id},
        ).mappings().first()

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active session not found",
        )

    return {
        "session_id": result["session_id"],
        "session_end_at": result["session_end_at"],
        "message": "Session ended successfully",
    }