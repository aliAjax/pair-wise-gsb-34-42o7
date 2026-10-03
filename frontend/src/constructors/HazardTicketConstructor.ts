import type { HazardTicket } from "../types/HazardTicket";

export const createDefaultHazardTicket = (
  overrides: Partial<HazardTicket> = {},
): HazardTicket => ({
  id: 0,
  result_id: 0,
  device_id: 0,
  task_id: 0,
  severity: "MEDIUM",
  owner_id: 0,
  deadline: "",
  rectify_status: "OPEN",
  rectify_note: "",
  closed_at: null,
  created_at: "",
  ...overrides,
});

export const createHazardTicketForm = createDefaultHazardTicket;
export const createHazardTicketResponse = createDefaultHazardTicket;
