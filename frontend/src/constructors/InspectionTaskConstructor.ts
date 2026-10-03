import type { InspectionTask } from "../types/InspectionTask";

export const createDefaultInspectionTask = (overrides: Partial<InspectionTask> = {}): InspectionTask => ({
  id: 1,
  building_id: 1,
  inspector_id: 1,
  plan_date: "2026-06-11T09:00:00Z",
  task_type: "HYDRANT",
  status: "IN_PROGRESS",
  checklist_version: "checklist version 1",
  revision: 1,
  finished_at: "",
  ...overrides
});

export const createInspectionTaskForm = createDefaultInspectionTask;
export const createInspectionTaskResponse = createDefaultInspectionTask;
