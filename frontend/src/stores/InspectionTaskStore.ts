import { create } from "zustand";
import {
  listInspectionTask, submitInspectionTask, reviewInspectionTask,
  rejectInspectionTask, listInspectionTaskConflicts, flushPendingSubmissions,
  pendingSubmissions
} from "../api/InspectionTask";
import type { SubmitTaskPayload, SubmitTaskResponse } from "../api/InspectionTask";
import type { InspectionTask } from "../types/InspectionTask";
import type { ConflictEntry } from "../types/ConflictEntry";

type State = {
  rows: InspectionTask[];
  conflicts: ConflictEntry[];
  pendingCount: number;
  loading: boolean;
  load: () => Promise<void>;
  submit: (taskId: number, payload: SubmitTaskPayload) => Promise<SubmitTaskResponse>;
  review: (taskId: number) => Promise<void>;
  reject: (taskId: number, itemCodes: string[], note?: string) => Promise<string[]>;
  loadConflicts: (taskId: number) => Promise<void>;
  flushPending: () => Promise<number>;
};

export const useInspectionTaskStore = create<State>((set, get) => ({
  rows: [],
  conflicts: [],
  pendingCount: 0,
  loading: false,
  async load() {
    set({ loading: true });
    set({
      rows: await listInspectionTask(),
      pendingCount: pendingSubmissions().length,
      loading: false
    });
  },
  async submit(taskId, payload) {
    const resp = await submitInspectionTask(taskId, payload);
    set({ pendingCount: pendingSubmissions().length });
    if (!resp.queued) await get().load();
    return resp;
  },
  async review(taskId) {
    await reviewInspectionTask(taskId);
    await get().load();
  },
  async reject(taskId, itemCodes, note = "") {
    const resp = await rejectInspectionTask(taskId, itemCodes, note);
    await get().load();
    return resp.reopened_items;
  },
  async loadConflicts(taskId) {
    set({ conflicts: await listInspectionTaskConflicts(taskId) });
  },
  async flushPending() {
    const flushed = await flushPendingSubmissions();
    set({ pendingCount: pendingSubmissions().length });
    if (flushed > 0) await get().load();
    return flushed;
  }
}));
