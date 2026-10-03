"""HTTP 鉴权中间件：尽力解析 JWT 并挂到 request.state.user；
严格权限判定仍由 auth_deps.get_current_user / allow_roles 在路由层完成。
"""

from src.utils.jwt_service import decode_access_token

_PUBLIC_PATHS = {"/health", "/api/auth/login", "/docs", "/openapi.json", "/redoc"}


async def auth_middleware(request, call_next):
    request.state.user = None
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        try:
            request.state.user = decode_access_token(auth[7:].strip())
        except ValueError:
            request.state.user = None
    if request.url.path in _PUBLIC_PATHS:
        return await call_next(request)
    # 中间件只做软注入；无 token 的写请求在路由依赖处被拒
    return await call_next(request)
