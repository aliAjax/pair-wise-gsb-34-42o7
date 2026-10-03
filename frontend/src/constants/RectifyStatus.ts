export const RectifyStatus = ["OPEN","RECTIFYING","CLOSED"] as const;
export type RectifyStatus = (typeof RectifyStatus)[number];
export const OPEN_RECTIFY_STATUSES: RectifyStatus[] = ["OPEN","RECTIFYING"];
export const RectifyStatusText: Record<RectifyStatus, string> = {
  OPEN: "待整改",
  RECTIFYING: "整改中",
  CLOSED: "已关闭"
};
