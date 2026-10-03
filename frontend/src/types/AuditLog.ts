export interface AuditLog {
  id: number;
  actor: number;
  role: string;
  action: string;
  entity: string;
  entity_id: number;
  detail: string;
  created_at: string;
}
