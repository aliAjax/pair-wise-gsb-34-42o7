import { getJson, postJson } from "./client";
import type { HazardTicket } from "../types/HazardTicket";

const endpoint = "/api/hazards";

export function listHazards(params?: {
  status?: string;
  device_id?: number;
}): Promise<HazardTicket[]> {
  const query = params
    ? "?" + new URLSearchParams(
        Object.entries(params)
          .filter(([, v]) => v !== undefined)
          .map(([k, v]) => [k, String(v)]),
      ).toString()
    : "";
  return getJson<HazardTicket[]>(`${endpoint}${query}`);
}

/** 物业主管派单。 */
export function assignHazard(hazardId: number, ownerId: number): Promise<HazardTicket> {
  return postJson<HazardTicket>(`${endpoint}/${hazardId}/assign`, { owner_id: ownerId });
}

/** 维保商整改提交。 */
export function rectifyHazard(hazardId: number, rectifyNote: string): Promise<HazardTicket> {
  return postJson<HazardTicket>(`${endpoint}/${hazardId}/rectify`, { rectify_note: rectifyNote });
}

/** 物业主管复验：approved=false 时退回维保商继续整改。 */
export function verifyHazard(
  hazardId: number,
  approved: boolean,
  note: string,
): Promise<HazardTicket> {
  return postJson<HazardTicket>(`${endpoint}/${hazardId}/verify`, { approved, note });
}
