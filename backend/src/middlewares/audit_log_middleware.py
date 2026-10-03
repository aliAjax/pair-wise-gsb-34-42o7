async def audit_log_middleware(request, call_next):
    print("audit", request.method, request.url.path)
    return await call_next(request)
