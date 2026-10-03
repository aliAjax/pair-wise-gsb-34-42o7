import { mockData } from "../mocks/seedData";
import { apiFetch } from "./client";
import type { InspectionTask } from "../types/InspectionTask";
import type { InspectionResult } from "../types/InspectionResult";
import type { HazardTicket } from "../types/HazardTicket";
import type { FireDevice } from "../types/FireDevice";
import type { ConflictEntry } from "../types/ConflictEntry";

const endpoint = "/api/inspection-task";

export interface SubmitResultItem {
  device_id: number;
  item_code: string;
  result_status: string;
  measured_value?: string;
  photo_url?: string;
  note?: string;
  severity?: string;
}

export interface SubmitTaskPayload {
  revision: number;
  submission_id: string;
  results: SubmitResultItem[];
}

export interface SubmitTaskResponse {
  task: InspectionTask;
  results: InspectionResult[];
  skipped_items: string[];
  hazards: HazardTicket[];
  devices: FireDevice[];
  replayed: boolean;
  queued?: boolean;
}

// 断网时完整任务快照留在本地队列，恢复后按原 submission_id 重投，服务端幂等
const QUEUE_KEY = "fire-inspect.pending-submissions";

interface QueuedSubmission {
  taskId: number;
  payload: SubmitTaskPayload;
}

function readQueue(): QueuedSubmission[] {
  try {
    return JSON.parse(localStorage.getItem(QUEUE_KEY) || "[]") as QueuedSubmission[];
  } catch {
    return [];
  }
}

function writeQueue(rows: QueuedSubmission[]) {
  localStorage.setItem(QUEUE_KEY, JSON.stringify(rows));
}

export function pendingSubmissions(): QueuedSubmission[] {
  return readQueue();
}

export async function listInspectionTask(): Promise<InspectionTask[]> {
  try {
    return await apiFetch<InspectionTask[]>(endpoint);
  } catch {
    // Local mock fallback keeps the UI available during offline review.
    return [...(mockData.inspectionTask as unknown as InspectionTask[])];
  }
}

export async function submitInspectionTask(
  taskId: number,
  payload: SubmitTaskPayload
): Promise<SubmitTaskResponse> {
  try {
    return await apiFetch<SubmitTaskResponse>(`${endpoint}/${taskId}/submit`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  } catch (err) {
    if (err instanceof TypeError) {
      // 网络中断：整包入队，恢复后由 flushPendingSubmissions 续投
      const queue = readQueue().filter((row) => row.payload.submission_id !== payload.submission_id);
      queue.push({ taskId, payload });
      writeQueue(queue);
      return { queued: true } as SubmitTaskResponse;
    }
    throw err;
  }
}

export async function flushPendingSubmissions(): Promise<number> {
  const queue = readQueue();
  let flushed = 0;
  const rest: QueuedSubmission[] = [];
  for (const row of queue) {
    try {
      await apiFetch<SubmitTaskResponse>(`${endpoint}/${row.taskId}/submit`, {
        method: "POST",
        body: JSON.stringify(row.payload)
      });
      flushed += 1;
    } catch (err) {
      if (err instanceof TypeError) {
        rest.push(row); // 仍断网，保留队列
      } else {
        rest.push(row); // 业务错误（如修订冲突）保留，交由冲突区处理
      }
    }
  }
  writeQueue(rest);
  return flushed;
}

export async function reviewInspectionTask(taskId: number): Promise<InspectionTask> {
  return apiFetch<InspectionTask>(`${endpoint}/${taskId}/review`, { method: "POST", body: "{}" });
}

export async function rejectInspectionTask(
  taskId: number,
  itemCodes: string[],
  note = ""
): Promise<{ task: InspectionTask; reopened_items: string[] }> {
  return apiFetch(`${endpoint}/${taskId}/reject`, {
    method: "POST",
    body: JSON.stringify({ item_codes: itemCodes, note })
  });
}

export async function listInspectionTaskConflicts(taskId: number): Promise<ConflictEntry[]> {
  return apiFetch<ConflictEntry[]>(`${endpoint}/${taskId}/conflicts`);
}

export async function saveInspectionTask(payload: InspectionTask) {
  console.info("save InspectionTask", payload);
  return payload;
}
