"""全局错误处理：统一错误码/错误消息结构。service/controller 仍可各自包装。"""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.constants import error_codes
from src.constants.error_messages import ERROR_MESSAGES
from src.domain import errors


def _payload(code: str, message: str, details=None) -> dict:
    return {
        "code": code,
        "message": message or ERROR_MESSAGES.get(code, message),
        "details": details or {},
    }


async def chain_error_handler(_request: Request, exc: errors.ChainError) -> JSONResponse:
    status_map = {
        error_codes.ERROR_CODES["AUTH_REQUIRED"]: 401,
        error_codes.ERROR_CODES["AUTH_INVALID"]: 401,
        error_codes.ERROR_CODES["RBAC_DENIED"]: 403,
        error_codes.ERROR_CODES["NOT_FOUND"]: 404,
        error_codes.ERROR_CODES["STALE_TASK_REVISION"]: 409,
        error_codes.ERROR_CODES["REVIEWED_PROTECTED"]: 409,
        error_codes.ERROR_CODES["STATE_CONFLICT"]: 409,
        error_codes.ERROR_CODES["REVIEW_TARGET_INVALID"]: 422,
        error_codes.ERROR_CODES["CHECKLIST_ITEM_INVALID"]: 422,
        error_codes.ERROR_CODES["HAZARD_NOT_OPEN"]: 409,
        error_codes.ERROR_CODES["VALIDATION_FAILED"]: 400,
    }
    code = getattr(exc, "code", error_codes.ERROR_CODES["INTERNAL_ERROR"])
    status_code = status_map.get(code, 500)
    return JSONResponse(
        status_code=status_code,
        content=_payload(code, str(exc), getattr(exc, "details", {})),
    )


async def validation_error_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=_payload(
            error_codes.ERROR_CODES["VALIDATION_FAILED"],
            ERROR_MESSAGES["VALIDATION_FAILED"],
            {"fields": exc.errors()[:20]},
        ),
    )


async def unhandled_error_handler(_request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=_payload(error_codes.ERROR_CODES["INTERNAL_ERROR"], str(exc)),
    )
