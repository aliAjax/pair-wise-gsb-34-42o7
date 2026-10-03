import { apiFetch } from "./client";
import type { AuditLog } from "../types/AuditLog";

const endpoint = "/api/audit-logs";

export async function listAuditLog(entity?: string, entityId?: number): Promise<AuditLog[]> {
  const query = entity && entityId ? `?entity=${entity}&entity_id=${entityId}` : "";
  return apiFetch<AuditLog[]>(`${endpoint}${query}`);
}
