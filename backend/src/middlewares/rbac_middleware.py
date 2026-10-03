"""RBAC 中间件工具：路由优先使用 auth_deps.allow_roles 依赖。

保留 allow_roles 函数式封装，供 controller/service 复用同一权限矩阵。
"""

from src.constants.user_role import UserRole
from src.domain import errors


# 角色 -> 允许的写动作前缀
ROLE_ACTION_MATRIX = {
    UserRole.INSPECTOR: ("InspectionTask.submit", "InspectionResult.update"),
    UserRole.MAINTAINER: ("HazardTicket.rectify",),
    UserRole.SUPERVISOR: (
        "InspectionTask.create",
        "InspectionTask.checklist_change",
        "InspectionResult.review",
        "HazardTicket.create",
        "HazardTicket.verify",
    ),
    UserRole.AUDITOR: (),
}


def allow_roles(*roles):
    """兼容旧桩：返回 checker，由路由显式调用。"""

    def checker(role: str) -> bool:
        if role not in roles:
            raise errors.RbacDeniedError(f"require one of {roles}, got {role}")
        return True

    return checker
