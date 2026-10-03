export const DeviceType = [
  "EXTINGUISHER",
  "HYDRANT",
  "SMOKE_DETECTOR",
  "SPRINKLER",
  "EXIT_LIGHT",
] as const;
export type DeviceType = (typeof DeviceType)[number];
export const DeviceTypeText: Record<DeviceType, string> = {
  EXTINGUISHER: "灭火器",
  HYDRANT: "消火栓",
  SMOKE_DETECTOR: "烟感探测器",
  SPRINKLER: "喷淋头",
  EXIT_LIGHT: "疏散指示灯",
};
