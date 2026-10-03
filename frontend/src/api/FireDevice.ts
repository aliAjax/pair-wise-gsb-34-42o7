import { getJson } from "./client";
import type { FireDevice } from "../types/FireDevice";

const endpoint = "/api/devices";

export function listFireDevices(params?: {
  building_id?: number;
  floor?: string;
}): Promise<FireDevice[]> {
  const query = params
    ? "?" + new URLSearchParams(
        Object.entries(params)
          .filter(([, v]) => v !== undefined && v !== "")
          .map(([k, v]) => [k, String(v)]),
      ).toString()
    : "";
  return getJson<FireDevice[]>(`${endpoint}${query}`);
}

export function getDeviceHistory(deviceId: number): Promise<{
  results: unknown[];
  hazards: unknown[];
}> {
  return getJson(`${endpoint}/${deviceId}/history`);
}
