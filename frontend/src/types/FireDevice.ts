export interface FireDevice {
  id: number;
  building_id: number;
  device_code: string;
  device_type: string;
  floor: string;
  location_desc: string;
  install_date: string;
  status: string;
  next_maintenance_at: string;
  open_hazard_count?: number;
  open_high_hazard_count?: number;
}
