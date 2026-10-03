from fastapi import APIRouter, Depends
from src.controllers.audit_log_controller import list_audit_log
from src.middlewares.rbac_middleware import allow_roles

router = APIRouter(prefix="/api/audit-logs", tags=["AuditLog"])
# 审计记录仅审计员可查
router.get("", dependencies=[Depends(allow_roles("AUDITOR", "ADMIN"))])(list_audit_log)
