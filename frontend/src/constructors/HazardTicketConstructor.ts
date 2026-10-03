import type { HazardTicket } from "../types/HazardTicket";

export const createDefaultHazardTicket = (overrides: Partial<HazardTicket> = {}): HazardTicket => ({
  id: 1 as never,
  result_id: 1 as never,
  severity: "severity 1" as never,
  owner_id: 1 as never,
  deadline: "deadline 1" as never,
  rectify_status: "IN_PROGRESS" as never,
  rectify_note: "rectify note 1" as never,
  closed_at: "2026-06-11T09:00:00Z" as never,
  ...overrides
});

export const createHazardTicketForm = createDefaultHazardTicket;
export const createHazardTicketResponse = createDefaultHazardTicket;
