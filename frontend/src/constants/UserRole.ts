export const UserRole = {
  INSPECTOR: "INSPECTOR",
  MAINTAINER: "MAINTAINER",
  SUPERVISOR: "SUPERVISOR",
  AUDITOR: "AUDITOR",
} as const;

export type UserRole = (typeof UserRole)[keyof typeof UserRole];

export const UserRoleText: Record<UserRole, string> = {
  INSPECTOR: "巡检员",
  MAINTAINER: "维保商",
  SUPERVISOR: "物业主管",
  AUDITOR: "审计员",
};
