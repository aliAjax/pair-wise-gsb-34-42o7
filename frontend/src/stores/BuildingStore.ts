import { create } from "zustand";
import { listBuildings } from "../api/Building";
import type { Building } from "../types/Building";

type State = {
  rows: Building[];
  loading: boolean;
  load: () => Promise<void>;
};

export const useBuildingStore = create<State>((set) => ({
  rows: [],
  loading: false,
  async load() {
    set({ loading: true });
    try {
      set({ rows: await listBuildings(), loading: false });
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },
}));
