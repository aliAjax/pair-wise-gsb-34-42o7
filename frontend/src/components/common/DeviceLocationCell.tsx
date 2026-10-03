import type { FireDevice } from "../../types/FireDevice";

export function DeviceLocationCell({ device }: { device: FireDevice }) {
  return <span>{device.floor} · {device.location_desc}</span>;
}
