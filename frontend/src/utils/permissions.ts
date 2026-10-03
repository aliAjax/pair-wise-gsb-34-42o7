import type { UserRole } from "../constants/UserRole";

/** 按钮显隐/路由守卫共用的权限矩阵，与后端 auth_deps 保持一致。 */
export const PERMISSIONS = {
  submitInspection: ["INSPECTOR"],
  reviewInspection: ["SUPERVISOR"],
  changeChecklist: ["SUPERVISOR"],
  assignHazard: ["SUPERVISOR"],
  rectifyHazard: ["MAINTAINER"],
  verifyHazard: ["SUPERVISOR"],
  viewAuditLog: ["AUDITOR", "SUPERVISOR"],
  readAll: ["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"],
} satisfies Record<string, UserRole["role"][] | string[]>;

export function can(role: string | undefined, action: keyof typeof PERMISSIONS): boolean {
  if (!role) return false;
  return PERMISSIONS[action].includes(role);
}
