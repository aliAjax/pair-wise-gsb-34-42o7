import type { InspectionResult } from "../types/InspectionResult";

export const createDefaultInspectionResult = (
  overrides: Partial<InspectionResult> = {},
): InspectionResult => ({
  id: 0,
  task_id: 0,
  device_id: 0,
  item_code: "",
  result_status: "PENDING",
  measured_value: "",
  photo_url: "",
  note: "",
  review_state: "DRAFT",
  severity_hint: "MEDIUM",
  revision: 1,
  submitted_at: null,
  reviewed_at: null,
  returned_at: null,
  ...overrides,
});

export const createInspectionResultForm = createDefaultInspectionResult;
export const createInspectionResultResponse = createDefaultInspectionResult;
