CREATE TABLE IF NOT EXISTS event_logs (
    event_id UUID PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    user_id UUID NULL,
    session_id UUID NULL,
    entity_type VARCHAR(50) NULL,
    entity_id UUID NULL,
    occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) NOT NULL,
    properties JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_event_logs_event_name
ON event_logs (event_name);

CREATE INDEX IF NOT EXISTS idx_event_logs_event_type
ON event_logs (event_type);

CREATE INDEX IF NOT EXISTS idx_event_logs_user_id
ON event_logs (user_id);

CREATE INDEX IF NOT EXISTS idx_event_logs_session_id
ON event_logs (session_id);

CREATE INDEX IF NOT EXISTS idx_event_logs_entity
ON event_logs (entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_event_logs_occurred_at
ON event_logs (occurred_at);