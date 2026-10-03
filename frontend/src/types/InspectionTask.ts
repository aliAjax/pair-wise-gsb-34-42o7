export interface ChecklistItem {
  item_code: string;
  device_id: number;
  title: string;
  default_severity: string;
  active: boolean;
}

export interface InspectionTask {
  id: number;
  building_id: number;
  inspector_id: number;
  plan_date: string;
  task_type: string;
  status: string;
  checklist_version: string;
  finished_at: string | null;
  revision: number;
  checklist_items: ChecklistItem[];
}

export interface FullInspectionTask extends InspectionTask {
  results: InspectionResultRef[];
}

export interface InspectionResultRef {
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
