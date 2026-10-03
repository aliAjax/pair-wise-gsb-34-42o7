export const HazardRectifyStatus = {
  OPEN: "OPEN",
  RECTIFIED: "RECTIFIED",
  CLOSED: "CLOSED",
  CANCELLED: "CANCELLED",
} as const;

export type HazardRectifyStatus =
  (typeof HazardRectifyStatus)[keyof typeof HazardRectifyStatus];

export const HazardRectifyStatusText: Record<HazardRectifyStatus, string> = {
  OPEN: "待整改",
  RECTIFIED: "待复验",
  CLOSED: "已关闭",
  CANCELLED: "已撤销",
};

export const OPEN_LIKE: HazardRectifyStatus[] = [
  HazardRectifyStatus.OPEN,
  HazardRectifyStatus.RECTIFIED,
];
