export interface HazardTicket {
  id: number;
  result_id: number;
  device_id: number;
  item_code: string;
  severity: string;
  owner_id: number;
  deadline: string;
  rectify_status: string;
  rectify_note: string;
  submission_id: string;
  closed_at: string;
}
