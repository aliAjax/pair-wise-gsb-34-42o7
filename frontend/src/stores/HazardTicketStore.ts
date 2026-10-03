import { create } from "zustand";
import { listHazards } from "../api/HazardTicket";
import type { HazardTicket } from "../types/HazardTicket";

type State = {
  rows: HazardTicket[];
  loading: boolean;
  load: (params?: { status?: string; device_id?: number }) => Promise<void>;
};

export const useHazardTicketStore = create<State>((set) => ({
  rows: [],
  loading: false,
  async load(params) {
    set({ loading: true });
    try {
      set({ rows: await listHazards(params), loading: false });
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },
}));
