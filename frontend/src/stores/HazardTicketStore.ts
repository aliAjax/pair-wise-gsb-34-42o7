import { create } from "zustand";
import { listHazardTicket } from "../api/HazardTicket";
import type { HazardTicket } from "../types/HazardTicket";

type State = { rows: HazardTicket[]; loading: boolean; load: () => Promise<void> };

export const useHazardTicketStore = create<State>((set) => ({
  rows: [],
  loading: false,
  async load() {
    set({ loading: true });
    set({ rows: await listHazardTicket(), loading: false });
  }
}));
