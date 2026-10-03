import { mockData } from "../mocks/seedData";
import { apiFetch } from "./client";
import type { InspectionResult } from "../types/InspectionResult";
import type { FireDevice } from "../types/FireDevice";

const endpoint = "/api/inspection-result";

export interface UpdateResultPayload {
  result_status?: string;
  measured_value?: string;
  photo_url?: string;
  note?: string;
  severity?: string;
}

export async function listInspectionResult(taskId?: number): Promise<InspectionResult[]> {
  try {
    const query = taskId ? `?task_id=${taskId}` : "";
    return await apiFetch<InspectionResult[]>(`${endpoint}${query}`);
  } catch {
    // Local mock fallback keeps the UI available during offline review.
    const rows = [...(mockData.inspectionResult as unknown as InspectionResult[])];
    return taskId ? rows.filter((row) => row.task_id === taskId) : rows;
  }
}

export async function updateInspectionResult(
  resultId: number,
  payload: UpdateResultPayload
): Promise<{ result: InspectionResult; device: FireDevice }> {
  return apiFetch(`${endpoint}/${resultId}`, {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}

export async function saveInspectionResult(payload: InspectionResult) {
  console.info("save InspectionResult", payload);
  return payload;
}
