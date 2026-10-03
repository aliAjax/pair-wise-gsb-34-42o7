import type { InspectionResult } from "../types/InspectionResult";

export const createDefaultInspectionResult = (overrides: Partial<InspectionResult> = {}): InspectionResult => ({
  id: 1,
  task_id: 1,
  device_id: 1,
  item_code: "PRESSURE",
  result_status: "NORMAL",
  measured_value: "measured value 1",
  photo_url: "/mock/photo_url-1.png",
  note: "note 1",
  submission_id: "",
  task_revision: 1,
  review_state: "PENDING",
  ...overrides
});

export const createInspectionResultForm = createDefaultInspectionResult;
export const createInspectionResultResponse = createDefaultInspectionResult;
