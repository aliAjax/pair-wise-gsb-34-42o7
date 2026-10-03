from fastapi import HTTPException, Request
from src.constants.error_codes import ERROR_CODES
from src.constants.error_messages import ERROR_MESSAGES

def allow_roles(*roles):
    """巡检员/维保商/审计员权限隔离：越权直接 403。"""
    allowed = {role.upper() for role in roles}
    async def dependency(request: Request):
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(status_code=401, detail={
                "code": ERROR_CODES["AUTH_REQUIRED"],
                "message": ERROR_MESSAGES["AUTH_REQUIRED"]
            })
        if user.get("role", "").upper() not in allowed:
            raise HTTPException(status_code=403, detail={
                "code": ERROR_CODES["RBAC_DENIED"],
                "message": ERROR_MESSAGES["RBAC_DENIED"]
            })
        return user
    return dependency
