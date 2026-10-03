export const ERROR_MESSAGES = {
  AUTH_REQUIRED: "请先登录后再继续操作",
  RBAC_DENIED: "当前角色没有执行该动作的权限",
  VALIDATION_FAILED: "表单字段缺失或格式错误",
  RATE_LIMITED: "请求过于频繁，请稍后再试",
  NOT_FOUND: "目标记录不存在",
  REVISION_CONFLICT: "任务修订号已过期，旧提交已进入冲突区，不能覆盖已复核结果",
  TASK_NOT_EDITABLE: "任务已提交或已复核，结果被冻结，请先由复核人退回",
  RESULT_LOCKED: "该检查项未被退回点名，保持已复核状态，禁止修改",
  HAZARD_STILL_OPEN: "存在未关闭的高危隐患，设备台账与合规报表不得显示正常"
};
