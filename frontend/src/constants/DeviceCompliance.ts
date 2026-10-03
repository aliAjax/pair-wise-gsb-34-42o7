export const DeviceCompliance = {
  ACTIVE: "ACTIVE",
  HAZARD_PENDING: "HAZARD_PENDING",
  HIGH_HAZARD_BLOCKED: "HIGH_HAZARD_BLOCKED",
  MAINTENANCE: "MAINTENANCE",
  RETIRED: "RETIRED",
} as const;

export type DeviceCompliance =
  (typeof DeviceCompliance)[keyof typeof DeviceCompliance];

export const DeviceComplianceText: Record<DeviceCompliance, string> = {
  ACTIVE: "正常",
  HAZARD_PENDING: "隐患未关闭",
  HIGH_HAZARD_BLOCKED: "高危隐患封锁",
  MAINTENANCE: "维保中",
  RETIRED: "停用",
};

export const ConflictReason = {
  STALE_TASK_REVISION: "STALE_TASK_REVISION",
  REVIEWED_PROTECTED: "REVIEWED_PROTECTED",
} as const;

export type ConflictReason =
  (typeof ConflictReason)[keyof typeof ConflictReason];

export const ConflictReasonText: Record<ConflictReason, string> = {
  STALE_TASK_REVISION: "任务修订号过期",
  REVIEWED_PROTECTED: "已复核结果受保护",
};
