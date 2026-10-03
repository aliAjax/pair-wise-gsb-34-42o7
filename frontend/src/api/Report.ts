import { apiFetch } from "./client";
import type { ComplianceReport } from "../types/ComplianceReport";

const endpoint = "/api/reports";

export async function getComplianceReport(): Promise<ComplianceReport> {
  return apiFetch<ComplianceReport>(`${endpoint}/compliance`);
}
