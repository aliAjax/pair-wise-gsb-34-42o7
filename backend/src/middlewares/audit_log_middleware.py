async def audit_log_middleware(request, call_next):
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        user = getattr(request.state, "user", {})
        print("audit", user.get("role", "-"), request.method, request.url.path)
    return await call_next(request)
