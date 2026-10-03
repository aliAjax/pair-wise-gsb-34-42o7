export interface HazardTicket {
  id: number;
  result_id: number;
  device_id: number;
  task_id: number;
  severity: string;
  owner_id: number;
  deadline: string;
  rectify_status: string;
  rectify_note: string;
  closed_at: string | null;
  created_at: string;
  device_code?: string;
}
