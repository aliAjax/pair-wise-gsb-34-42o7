import { create } from "zustand";
import { listInspectionResult, updateInspectionResult } from "../api/InspectionResult";
import type { UpdateResultPayload } from "../api/InspectionResult";
import type { InspectionResult } from "../types/InspectionResult";
import type { FireDevice } from "../types/FireDevice";

type State = {
  rows: InspectionResult[];
  loading: boolean;
  load: (taskId?: number) => Promise<void>;
  update: (resultId: number, payload: UpdateResultPayload) => Promise<FireDevice | undefined>;
};

export const useInspectionResultStore = create<State>((set, get) => ({
  rows: [],
  loading: false,
  async load(taskId) {
    set({ loading: true });
    set({ rows: await listInspectionResult(taskId), loading: false });
  },
  async update(resultId, payload) {
    const resp = await updateInspectionResult(resultId, payload);
    await get().load();
    return resp.device;
  }
}));
