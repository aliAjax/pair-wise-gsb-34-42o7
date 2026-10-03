"""FastAPI 入口：中间件、错误处理、路由、启动建表与种子。"""

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.config.database import init_schema
from src.config.settings import settings
from src.domain import errors
from src.middlewares.audit_log_middleware import audit_log_middleware
from src.middlewares.auth_middleware import auth_middleware
from src.middlewares.error_handler_middleware import (
    chain_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from src.middlewares.rate_limit_middleware import rate_limit_middleware
from src.middlewares.request_logger_middleware import request_logger_middleware
from src.routes.auth_routes import router as auth_router
from src.routes.building_routes import router as building_router
from src.routes.compliance_routes import router as compliance_router
from src.routes.fire_device_routes import router as fire_device_router
from src.routes.hazard_ticket_routes import router as hazard_ticket_router
from src.routes.inspection_result_routes import router as inspection_result_router
from src.routes.inspection_task_routes import router as inspection_task_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="消防设施巡检维保平台 - 复核链", version="1.1.0")

# 中间件执行顺序：后注册的先执行（洋葱外层）
app.middleware("http")(request_logger_middleware)
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(audit_log_middleware)
app.middleware("http")(auth_middleware)

app.add_exception_handler(errors.ChainError, chain_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)


@app.on_event("startup")
def _on_startup():
    init_schema()
    if settings.SEED_ON_START:
        from src.seed import seed_database

        seed_database()


@app.get("/health")
def health():
    return {"status": "ok", "service": "fire-inspect", "revision_chain": True}


for router in (
    auth_router,
    building_router,
    fire_device_router,
    inspection_task_router,
    inspection_result_router,
    hazard_ticket_router,
    compliance_router,
):
    app.include_router(router)
