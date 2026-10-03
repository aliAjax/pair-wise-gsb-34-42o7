import type { InspectionResult } from "../types/InspectionResult";

export const createDefaultInspectionResult = (overrides: Partial<InspectionResult> = {}): InspectionResult => ({
  id: 1 as never,
  task_id: 1 as never,
  device_id: 1 as never,
  item_code: "item code 1" as never,
  result_status: "IN_PROGRESS" as never,
  measured_value: "measured value 1" as never,
  photo_url: "/mock/photo_url-1.png" as never,
  note: "note 1" as never,
  ...overrides
});

export const createInspectionResultForm = createDefaultInspectionResult;
export const createInspectionResultResponse = createDefaultInspectionResult;
