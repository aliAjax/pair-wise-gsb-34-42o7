export interface FireDevice {
  id: number;
  building_id: number;
  device_code: string;
  device_type: string;
  floor: string;
  location_desc: string;
  install_date: string;
  /** 台账展示状态：由未关闭隐患实时重算（高危隐患封锁时不会是 ACTIVE） */
  status: string;
  /** 主数据状态：NORMAL / MAINTENANCE / RETIRED */
  base_status: string;
  next_maintenance_at: string | null;
  owner_id: number | null;
}
