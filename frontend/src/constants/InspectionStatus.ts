export const InspectionStatus = [
  "PLANNED",
  "IN_PROGRESS",
  "SUBMITTED",
  "REVIEWED",
  "RETURNED",
  "OVERDUE",
] as const;
export type InspectionStatus = (typeof InspectionStatus)[number];
export const InspectionStatusText: Record<InspectionStatus, string> = {
  PLANNED: "已排期",
  IN_PROGRESS: "巡检中",
  SUBMITTED: "待复核",
  REVIEWED: "已复核",
  RETURNED: "已退回重开",
  OVERDUE: "已逾期",
};
