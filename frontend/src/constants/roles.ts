export const Roles = ["INSPECTOR","MAINTAINER","AUDITOR","ADMIN"] as const;
export type Role = (typeof Roles)[number];
export const RoleText: Record<Role, string> = {
  INSPECTOR: "巡检员",
  MAINTAINER: "维保商",
  AUDITOR: "审计员",
  ADMIN: "物业主管"
};
// 复核链权限隔离：提交/改项 = 巡检员，复核/退回/审计 = 审计员，关单 = 维保商
export const ROLE_PERMISSIONS: Record<Role, string[]> = {
  INSPECTOR: ["task:submit","result:update"],
  MAINTAINER: ["hazard:close"],
  AUDITOR: ["task:review","task:reject","audit:view","report:view"],
  ADMIN: ["task:submit","result:update","hazard:close","task:review","task:reject","audit:view","report:view"]
};
export const can = (role: Role, permission: string) =>
  ROLE_PERMISSIONS[role]?.includes(permission) ?? false;
