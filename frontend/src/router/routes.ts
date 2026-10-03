export const routes = [
  {
    name: "消防合规总览",
    route: "/dashboard",
    roles: ["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"],
  },
  {
    name: "消防设备台账",
    route: "/devices",
    roles: ["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"],
  },
  { name: "巡检任务", route: "/tasks", roles: ["INSPECTOR", "SUPERVISOR"] },
  { name: "隐患整改", route: "/hazards", roles: ["MAINTAINER", "SUPERVISOR", "AUDITOR"] },
  {
    name: "合规报表",
    route: "/reports",
    roles: ["INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR"],
  },
  { name: "审计日志", route: "/audit", roles: ["SUPERVISOR", "AUDITOR"] },
] as const;
