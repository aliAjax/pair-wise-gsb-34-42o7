export interface BuildingCompliance {
  building_id: number;
  building_name: string;
  task_total: number;
  task_reviewed: number;
  review_rate: number;
  hazard_total: number;
  hazard_closed: number;
  rectify_rate: number;
  device_total: number;
  device_abnormal: number;
  device_fault_rate: number;
  open_high_hazards: number;
  compliance_status: string;
}

export interface ComplianceReport {
  buildings: BuildingCompliance[];
  devices: import("./FireDevice").FireDevice[];
  summary: {
    open_high_hazards: number;
    device_abnormal: number;
    compliance_status: string;
  };
}
