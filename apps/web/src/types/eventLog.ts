export type EventLogType = "user_behavior" | "domain_event" | "system_event";

export type EventLogSource = "frontend" | "backend" | "script";

export type EventLogCreateRequest = {
  event_name: string;
  event_type: EventLogType;
  source: EventLogSource;
  user_id?: string | null;
  session_id?: string | null;
  entity_type?: string | null;
  entity_id?: string | null;
  properties?: Record<string, unknown>;
};

export type EventLogCreateResponse = {
  event_id: string;
  event_name: string;
  event_type: EventLogType;
  user_id: string | null;
  session_id: string | null;
  entity_type: string | null;
  entity_id: string | null;
  occurred_at: string;
  source: EventLogSource;
  properties: Record<string, unknown>;
  created_at: string;
  message: string;
};