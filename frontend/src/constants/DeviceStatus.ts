export const DeviceStatus = ["NORMAL","MAINTENANCE","ABNORMAL"] as const;
export type DeviceStatus = (typeof DeviceStatus)[number];
export const DeviceStatusText: Record<DeviceStatus, string> = {
  NORMAL: "正常",
  MAINTENANCE: "待维保",
  ABNORMAL: "异常"
};
