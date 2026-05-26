import type {
  EventLogCreateRequest,
  EventLogCreateResponse,
} from "../types/eventLog";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function recordUserBehaviorEvent(
  payload: Omit<EventLogCreateRequest, "event_type" | "source">,
): Promise<EventLogCreateResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/events`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...payload,
        event_type: "user_behavior",
        source: "frontend",
        properties: payload.properties ?? {},
      }),
    });

    if (!response.ok) {
      console.error("Failed to record user behavior event", response.status);
      return null;
    }

    return (await response.json()) as EventLogCreateResponse;
  } catch (error) {
    console.error("Failed to record user behavior event", error);
    return null;
  }
}