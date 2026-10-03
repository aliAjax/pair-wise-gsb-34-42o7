import { getJson } from "./client";
import type { InspectionResult } from "../types/InspectionResult";

export function listInspectionResults(taskId?: number): Promise<InspectionResult[]> {
  const suffix = taskId ? `?task_id=${taskId}` : "";
  return getJson<InspectionResult[]>(`/api/inspection-results${suffix}`);
}
