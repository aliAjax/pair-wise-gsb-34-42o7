async def auth_middleware(request, call_next):
    role = (request.headers.get("x-role") or "INSPECTOR").upper()
    raw_id = request.headers.get("x-user-id") or "1"
    request.state.user = {"id": int(raw_id) if raw_id.isdigit() else 1, "role": role}
    return await call_next(request)
