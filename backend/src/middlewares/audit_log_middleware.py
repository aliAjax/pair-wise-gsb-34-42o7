"""审计日志 HTTP 中间件：记录请求骨架；业务细粒度审计在 service 层落 audit_log。"""

import logging
import time

logger = logging.getLogger("fire_inspect.audit")

_WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


async def audit_log_middleware(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    if request.method in _WRITE_METHODS and request.url.path.startswith("/api"):
        user = getattr(request.state, "user", None)
        logger.info(
            "audit-http actor=%s role=%s %s %s status=%s %.0fms",
            (user or {}).get("sub", "anonymous"),
            (user or {}).get("role", "-"),
            request.method,
            request.url.path,
            response.status_code,
            (time.perf_counter() - started) * 1000,
        )
    return response
