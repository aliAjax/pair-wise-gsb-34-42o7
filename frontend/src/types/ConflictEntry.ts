export interface ConflictEntry {
  id: number;
  task_id: number;
  submission_id: string;
  revision: number;
  current_revision: number;
  reason: string;
  created_at: string;
}
