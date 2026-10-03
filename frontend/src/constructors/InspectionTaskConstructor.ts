import type { InspectionTask } from "../types/InspectionTask";

export const createDefaultInspectionTask = (
  overrides: Partial<InspectionTask> = {},
): InspectionTask => ({
  id: 0,
  building_id: 1,
  inspector_id: 1,
  plan_date: "2026-10-03",
  task_type: "ROUTINE",
  status: "PLANNED",
  checklist_version: "v1",
  finished_at: null,
  revision: 1,
  checklist_items: [],
  ...overrides,
});

export const createInspectionTaskForm = createDefaultInspectionTask;
export const createInspectionTaskResponse = createDefaultInspectionTask;
