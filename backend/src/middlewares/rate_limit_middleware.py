"""简单内存限流：按 IP+路径桶统计；多实例可替换为 Redis。"""

import threading
import time

from fastapi.responses import JSONResponse

from src.config.settings import settings
from src.constants import error_codes
from src.constants.error_messages import ERROR_MESSAGES


class _SlidingWindow:
    def __init__(self):
        self._hits: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str, limit: int, window: float = 60.0) -> bool:
        now = time.time()
        with self._lock:
            bucket = [t for t in self._hits.get(key, []) if now - t < window]
            if len(bucket) >= limit:
                self._hits[key] = bucket
                return False
            bucket.append(now)
            self._hits[key] = bucket
            return True


_window = _SlidingWindow()


async def rate_limit_middleware(request, call_next):
    if request.url.path.startswith("/api"):
        key = f"{request.client.host if request.client else 'local'}:{request.url.path}"
        if not _window.allow(key, settings.RATE_LIMIT_PER_MINUTE):
            return JSONResponse(
                status_code=429,
                content={
                    "code": error_codes.ERROR_CODES["RATE_LIMITED"],
                    "message": ERROR_MESSAGES["RATE_LIMITED"],
                    "details": {"limit_per_minute": settings.RATE_LIMIT_PER_MINUTE},
                },
            )
    return await call_next(request)
