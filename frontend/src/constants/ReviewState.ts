export const ReviewState = ["PENDING","SUBMITTED","REVIEWED","REOPENED"] as const;
export type ReviewState = (typeof ReviewState)[number];
export const EDITABLE_REVIEW_STATES: ReviewState[] = ["PENDING","REOPENED"];
export const ReviewStateText: Record<ReviewState, string> = {
  PENDING: "待提交",
  SUBMITTED: "已提交",
  REVIEWED: "已复核",
  REOPENED: "退回重开"
};
