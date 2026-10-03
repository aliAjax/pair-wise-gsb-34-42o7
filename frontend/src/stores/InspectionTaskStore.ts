import { create } from "zustand";
import { listInspectionTask } from "../api/InspectionTask";
import type { InspectionTask } from "../types/InspectionTask";

type State = {
  rows: InspectionTask[];
  loading: boolean;
  load: (params?: { building_id?: number; inspector_id?: number }) => Promise<void>;
};

export const useInspectionTaskStore = create<State>((set) => ({
  rows: [],
  loading: false,
  async load(params) {
    set({ loading: true });
    try {
      set({ rows: await listInspectionTask(params), loading: false });
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },
}));
