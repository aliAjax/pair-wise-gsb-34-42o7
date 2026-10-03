export interface InspectionResult {
  id: number;
  task_id: number;
  device_id: number;
  item_code: string;
  result_status: string;
  measured_value: string;
  photo_url: string;
  note: string;
  review_state: string;
  severity_hint: string;
  revision: number;
  submitted_at: string | null;
  reviewed_at: string | null;
  returned_at: string | null;
}

export interface SubmitItem {
  item_code: string;
  result_status: string;
  measured_value?: string;
  photo_url?: string;
  note?: string;
  severity_hint?: string | null;
  owner_id?: number | null;
  deadline?: string | null;
}

export interface SubmitTaskRequest {
  client_submission_id: string;
  base_revision: number;
  items: SubmitItem[];
}

export interface SubmissionOutcome {
  state: "ACCEPTED" | "PARTIAL" | "CONFLICT" | "REPLAYED";
  task_id: number;
  base_revision: number;
  new_revision: number;
  accepted_items: string[];
  conflicts: { item_code: string; reason: string }[];
  hazard_ids_created: number[];
  hazard_ids_cancelled: number[];
  replayed: boolean;
}
