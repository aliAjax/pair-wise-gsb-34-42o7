import { create } from "zustand";
import { listInspectionTask } from "../api/InspectionTask";
import type { InspectionTask } from "../types/InspectionTask";

type State = { rows: InspectionTask[]; loading: boolean; load: () => Promise<void> };

export const useInspectionTaskStore = create<State>((set) => ({
  rows: [],
  loading: false,
  async load() {
    set({ loading: true });
    set({ rows: await listInspectionTask(), loading: false });
  }
}));
