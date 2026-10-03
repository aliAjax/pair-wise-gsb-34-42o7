import { create } from "zustand";
import { listHazardTicket, closeHazardTicket } from "../api/HazardTicket";
import type { HazardTicket } from "../types/HazardTicket";

type State = {
  rows: HazardTicket[];
  loading: boolean;
  load: () => Promise<void>;
  close: (ticketId: number, rectifyNote: string) => Promise<void>;
};

export const useHazardTicketStore = create<State>((set, get) => ({
  rows: [],
  loading: false,
  async load() {
    set({ loading: true });
    set({ rows: await listHazardTicket(), loading: false });
  },
  async close(ticketId, rectifyNote) {
    await closeHazardTicket(ticketId, rectifyNote);
    await get().load();
  }
}));
