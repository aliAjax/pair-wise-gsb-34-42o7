import type { FireDevice } from "../types/FireDevice";

export const createDefaultFireDevice = (
  overrides: Partial<FireDevice> = {},
): FireDevice => ({
  id: 0,
  building_id: 1,
  device_code: "",
  device_type: "HYDRANT",
  floor: "1",
  location_desc: "",
  install_date: "2026-01-01",
  status: "ACTIVE",
  base_status: "NORMAL",
  next_maintenance_at: null,
  owner_id: null,
  ...overrides,
});

export const createFireDeviceForm = createDefaultFireDevice;
export const createFireDeviceResponse = createDefaultFireDevice;
