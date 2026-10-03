import { mockData } from "../mocks/seedData";
import { apiFetch } from "./client";
import type { HazardTicket } from "../types/HazardTicket";
import type { FireDevice } from "../types/FireDevice";

const endpoint = "/api/hazard-ticket";

export async function listHazardTicket(): Promise<HazardTicket[]> {
  try {
    return await apiFetch<HazardTicket[]>(endpoint);
  } catch {
    // Local mock fallback keeps the UI available during offline review.
    return [...(mockData.hazardTicket as unknown as HazardTicket[])];
  }
}

export async function closeHazardTicket(
  ticketId: number,
  rectifyNote: string
): Promise<{ ticket: HazardTicket; device: FireDevice }> {
  return apiFetch(`${endpoint}/${ticketId}/close`, {
    method: "POST",
    body: JSON.stringify({ rectify_note: rectifyNote })
  });
}

export async function saveHazardTicket(payload: HazardTicket) {
  console.info("save HazardTicket", payload);
  return payload;
}
