export interface SubmissionConflict {
  id: number;
  task_id: number;
  client_submission_id: string;
  base_revision: number;
  current_revision: number;
  reason: string;
  payload_preview: string;
  created_at: string;
}

export interface AuditLogEntry {
  id: number;
  actor_id: number;
  actor_role: string;
  action: string;
  target_type: string;
  target_id: string;
  detail: string;
  created_at: string;
}

export interface AuthUser {
  id: number;
  username: string;
  display_name: string;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface DashboardSummary {
  device_total: number;
  open_hazard_total: number;
  open_high_risk_hazards: number;
  high_risk_blocked_devices: number;
  blocked_device_ids: number[];
  task_total: number;
  task_reviewed: number;
  inspection_completion_rate: number;
  [key: string]: unknown;
}
