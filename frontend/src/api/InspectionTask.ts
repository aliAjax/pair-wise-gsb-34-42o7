import { getJson, patchJson, postJson } from "./client";
import type {
  FullInspectionTask,
  InspectionTask,
} from "../types/InspectionTask";
import type { SubmissionOutcome, SubmitTaskRequest } from "../types/InspectionResult";
import type { SubmissionConflict } from "../types/Chain";

const endpoint = "/api/inspection-tasks";

export function listInspectionTask(params?: {
  building_id?: number;
  inspector_id?: number;
}): Promise<InspectionTask[]> {
  const query = params
    ? "?" + new URLSearchParams(
        Object.entries(params)
          .filter(([, v]) => v !== undefined)
          .map(([k, v]) => [k, String(v)]),
      ).toString()
    : "";
  return getJson<InspectionTask[]>(`${endpoint}${query}`);
}

export function createInspectionTask(body: {
  building_id: number;
  inspector_id: number;
  plan_date: string;
  task_type?: string;
  checklist_items: {
    item_code: string;
    device_id: number;
    title: string;
    default_severity: string;
  }[];
}): Promise<InspectionTask> {
  return postJson<InspectionTask>(endpoint, body);
}

/** 断网恢复后先拉完整任务（修订号 + 全量检查项/结果），再继续提交。 */
export function getFullTask(taskId: number): Promise<FullInspectionTask> {
  return getJson<FullInspectionTask>(`${endpoint}/${taskId}/full`);
}

/** 提交：携带 base_revision 与 client_submission_id（幂等）。 */
export function submitTask(taskId: number, body: SubmitTaskRequest): Promise<SubmissionOutcome> {
  return postJson<SubmissionOutcome>(`${endpoint}/${taskId}/submissions`, body);
}

/** 复核：APPROVE / RETURN；RETURN 只放开 item_codes 中点名的检查项。 */
export function reviewTask(
  taskId: number,
  body: { decision: "APPROVE" | "RETURN"; item_codes: string[]; note?: string },
): Promise<{
  decision: string;
  item_codes: string[];
  new_revision: number;
  task_status: string;
}> {
  return postJson(`${endpoint}/${taskId}/reviews`, body);
}

/** 检查项增删改：服务端自增修订号，并重算隐患与设备状态。 */
export function changeChecklist(
  taskId: number,
  body: {
    added?: { item_code: string; device_id: number; title: string; default_severity: string }[];
    removed?: string[];
    updated?: { item_code: string; title?: string; default_severity?: string }[];
  },
): Promise<Record<string, unknown>> {
  return patchJson(`${endpoint}/${taskId}/checklist`, body);
}

export function listConflictZone(taskId?: number): Promise<SubmissionConflict[]> {
  const suffix = taskId ? `?task_id=${taskId}` : "";
  return getJson<SubmissionConflict[]>(`${endpoint}/conflicts/zone${suffix}`);
}
