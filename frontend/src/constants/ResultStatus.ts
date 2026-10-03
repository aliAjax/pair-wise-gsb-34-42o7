export const ResultStatus = {
  PENDING: "PENDING",
  NORMAL: "NORMAL",
  ABNORMAL: "ABNORMAL",
} as const;

export type ResultStatus = (typeof ResultStatus)[keyof typeof ResultStatus];

export const ResultStatusText: Record<ResultStatus, string> = {
  PENDING: "待检",
  NORMAL: "正常",
  ABNORMAL: "异常",
};
