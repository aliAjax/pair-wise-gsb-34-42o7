"""请求日志中间件。"""

import logging
import time

logger = logging.getLogger("fire_inspect.request")


async def request_logger_middleware(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    logger.info(
        "%s %s -> %s %.0fms",
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - started) * 1000,
    )
    return response
