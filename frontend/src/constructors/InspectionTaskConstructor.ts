import type { InspectionTask } from "../types/InspectionTask";

export const createDefaultInspectionTask = (overrides: Partial<InspectionTask> = {}): InspectionTask => ({
  id: 1 as never,
  building_id: 1 as never,
  inspector_id: 1 as never,
  plan_date: "2026-06-11T09:00:00Z" as never,
  task_type: "HYDRANT" as never,
  status: "IN_PROGRESS" as never,
  checklist_version: "checklist version 1" as never,
  finished_at: "2026-06-11T09:00:00Z" as never,
  ...overrides
});

export const createInspectionTaskForm = createDefaultInspectionTask;
export const createInspectionTaskResponse = createDefaultInspectionTask;
