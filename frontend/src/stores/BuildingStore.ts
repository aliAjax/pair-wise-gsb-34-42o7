import { create } from "zustand";
import { listBuilding } from "../api/Building";
import type { Building } from "../types/Building";

type State = { rows: Building[]; loading: boolean; load: () => Promise<void> };

export const useBuildingStore = create<State>((set) => ({
  rows: [],
  loading: false,
  async load() {
    set({ loading: true });
    set({ rows: await listBuilding(), loading: false });
  }
}));
