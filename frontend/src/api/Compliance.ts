import { getJson } from "./client";
import type { AuditLogEntry, DashboardSummary } from "../types/Chain";

export function getDashboard(): Promise<DashboardSummary> {
  return getJson<DashboardSummary>("/api/dashboard");
}

export function getMonthlyReport(): Promise<Record<string, unknown>> {
  return getJson("/api/reports/monthly");
}

export function listAuditLogs(params?: {
  target_type?: string;
  target_id?: string;
}): Promise<AuditLogEntry[]> {
  const query = params
    ? "?" + new URLSearchParams(
        Object.entries(params)
          .filter(([, v]) => v !== undefined && v !== "")
          .map(([k, v]) => [k, String(v)]),
      ).toString()
    : "";
  return getJson<AuditLogEntry[]>(`/api/audit-logs${query}`);
}
