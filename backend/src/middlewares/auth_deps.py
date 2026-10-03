"""FastAPI 鉴权与 RBAC 依赖。权限矩阵：

- INSPECTOR 巡检员：领取任务、提交/续传巡检结果
- MAINTAINER 维保商：隐患整改（rectify）
- SUPERVISOR 物业主管：复核、检查项修改、派单、复验关闭
- AUDITOR 审计员：全局只读 + 审计日志查询
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, Request

from src.domain import errors
from src.utils.jwt_service import decode_access_token


@dataclass
class CurrentUser:
    id: int
    username: str
    role: str


def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None),
    x_role: str | None = Header(default=None),
) -> CurrentUser:
    token = ""
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_role and request.headers.get("x-dev-token") == "local-dev":
        # 本地联调旁路：必须同时给出 x-dev-token，禁止生产使用
        user_id = int(request.headers.get("x-user-id", "0") or 0)
        return CurrentUser(id=user_id, username=f"dev-{x_role}", role=x_role)

    if not token:
        raise errors.AuthRequiredError()
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise errors.AuthInvalidError(str(exc)) from exc
    return CurrentUser(
        id=int(payload["sub"]),
        username=payload.get("username", ""),
        role=payload.get("role", ""),
    )


def allow_roles(*roles: str):
    def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise errors.RbacDeniedError(
                f"role {user.role} cannot access, require one of {roles}",
                details={"required": list(roles), "actual": user.role},
            )
        return user

    return checker
