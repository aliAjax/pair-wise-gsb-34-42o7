# 角色：巡检员 / 维保商 / 审计员 / 物业主管，权限互相隔离
Roles = ["INSPECTOR","MAINTAINER","AUDITOR","ADMIN"]
ROLE_PERMISSIONS = {
  "INSPECTOR": ["task:submit","result:update"],
  "MAINTAINER": ["hazard:close"],
  "AUDITOR": ["task:review","task:reject","audit:view","report:view"],
  "ADMIN": ["task:submit","result:update","hazard:close","task:review","task:reject","audit:view","report:view"]
}
