import { create } from "zustand";
import { listInspectionResults } from "../api/InspectionResult";
import type { InspectionResult } from "../types/InspectionResult";

type State = {
  rows: InspectionResult[];
  loading: boolean;
  load: (taskId?: number) => Promise<void>;
};

export const useInspectionResultStore = create<State>((set) => ({
  rows: [],
  loading: false,
  async load(taskId) {
    set({ loading: true });
    try {
      set({ rows: await listInspectionResults(taskId), loading: false });
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },
}));
