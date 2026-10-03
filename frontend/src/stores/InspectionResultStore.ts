import { create } from "zustand";
import { listInspectionResult } from "../api/InspectionResult";
import type { InspectionResult } from "../types/InspectionResult";

type State = { rows: InspectionResult[]; loading: boolean; load: () => Promise<void> };

export const useInspectionResultStore = create<State>((set) => ({
  rows: [],
  loading: false,
  async load() {
    set({ loading: true });
    set({ rows: await listInspectionResult(), loading: false });
  }
}));
