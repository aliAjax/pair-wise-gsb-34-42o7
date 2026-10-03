"""复核链领域异常。service/controller 必须各自包装，禁止在全局一处吞掉。"""

from src.constants import error_codes


class ChainError(Exception):
    code = error_codes.ERROR_CODES["INTERNAL_ERROR"]

    def __init__(self, message: str = "", *, details=None):
        super().__init__(message or self.__class__.__name__)
        self.details = details or {}


class AuthRequiredError(ChainError):
    code = error_codes.ERROR_CODES["AUTH_REQUIRED"]


class AuthInvalidError(ChainError):
    code = error_codes.ERROR_CODES["AUTH_INVALID"]


class RbacDeniedError(ChainError):
    code = error_codes.ERROR_CODES["RBAC_DENIED"]


class NotFoundError(ChainError):
    code = error_codes.ERROR_CODES["NOT_FOUND"]


class StateConflictError(ChainError):
    code = error_codes.ERROR_CODES["STATE_CONFLICT"]


class StaleRevisionError(ChainError):
    code = error_codes.ERROR_CODES["STALE_TASK_REVISION"]


class ReviewedProtectedError(ChainError):
    code = error_codes.ERROR_CODES["REVIEWED_PROTECTED"]


class ReviewTargetError(ChainError):
    code = error_codes.ERROR_CODES["REVIEW_TARGET_INVALID"]


class ChecklistItemError(ChainError):
    code = error_codes.ERROR_CODES["CHECKLIST_ITEM_INVALID"]


class HazardStateError(ChainError):
    code = error_codes.ERROR_CODES["HAZARD_NOT_OPEN"]


class ValidationChainError(ChainError):
    code = error_codes.ERROR_CODES["VALIDATION_FAILED"]
