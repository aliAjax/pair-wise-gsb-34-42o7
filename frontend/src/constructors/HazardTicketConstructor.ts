import type { HazardTicket } from "../types/HazardTicket";

export const createDefaultHazardTicket = (overrides: Partial<HazardTicket> = {}): HazardTicket => ({
  id: 1,
  result_id: 1,
  device_id: 1,
  item_code: "PRESSURE",
  severity: "MEDIUM",
  owner_id: 1,
  deadline: "2026-10-10T09:00:00Z",
  rectify_status: "OPEN",
  rectify_note: "",
  submission_id: "",
  closed_at: "",
  ...overrides
});

export const createHazardTicketForm = createDefaultHazardTicket;
export const createHazardTicketResponse = createDefaultHazardTicket;
