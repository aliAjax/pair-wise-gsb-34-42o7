export const ReviewState = {
  DRAFT: "DRAFT",
  SUBMITTED: "SUBMITTED",
  REVIEWED: "REVIEWED",
  RETURNED: "RETURNED",
  DISCARDED: "DISCARDED",
} as const;

export type ReviewState = (typeof ReviewState)[keyof typeof ReviewState];

export const ReviewStateText: Record<ReviewState, string> = {
  DRAFT: "暂存",
  SUBMITTED: "待复核",
  REVIEWED: "已复核",
  RETURNED: "已退回",
  DISCARDED: "已废弃",
};

export const ReviewDecision = {
  APPROVE: "APPROVE",
  RETURN: "RETURN",
} as const;

export type ReviewDecision = (typeof ReviewDecision)[keyof typeof ReviewDecision];
