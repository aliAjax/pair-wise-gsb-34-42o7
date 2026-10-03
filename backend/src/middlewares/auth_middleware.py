async def auth_middleware(request, call_next):
    request.state.user = {"id": 1, "role": request.headers.get("x-role", "admin")}
    return await call_next(request)
