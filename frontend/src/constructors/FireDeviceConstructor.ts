import type { FireDevice } from "../types/FireDevice";

export const createDefaultFireDevice = (overrides: Partial<FireDevice> = {}): FireDevice => ({
  id: 1,
  building_id: 1,
  device_code: "device code 1",
  device_type: "HYDRANT",
  floor: "floor 1",
  location_desc: "location desc 1",
  install_date: "2026-06-11T09:00:00Z",
  status: "NORMAL",
  next_maintenance_at: "2026-06-11T09:00:00Z",
  open_hazard_count: 0,
  open_high_hazard_count: 0,
  ...overrides
});

export const createFireDeviceForm = createDefaultFireDevice;
export const createFireDeviceResponse = createDefaultFireDevice;
