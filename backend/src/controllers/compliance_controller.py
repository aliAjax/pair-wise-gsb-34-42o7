"""合规报表 controller 与审计日志查询（审计员只读）。"""

from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.constants.user_role import UserRole
from src.constructors.chain_dto_builder import build_audit_dto
from src.middlewares.auth_deps import CurrentUser, allow_roles
from src.services.compliance_app_service import ComplianceAppService
from src.services.chain_service import ChainService

_reader = allow_roles(UserRole.INSPECTOR, UserRole.MAINTAINER, UserRole.SUPERVISOR, UserRole.AUDITOR)


def dashboard_controller(
    db: Session = Depends(get_db),
    _user: CurrentUser = Depends(_reader),
):
    return ComplianceAppService(db).dashboard()


def monthly_report_controller(
    db: Session = Depends(get_db),
    _user: CurrentUser = Depends(_reader),
):
    return ComplianceAppService(db).monthly_report()


def list_audit_logs_controller(
    target_type: str | None = None,
    target_id: str | None = None,
    db: Session = Depends(get_db),
    _user: CurrentUser = Depends(allow_roles(UserRole.AUDITOR, UserRole.SUPERVISOR)),
):
    rows = ChainService(db).audit_logs(target_id=target_id, target_type=target_type)
    return [build_audit_dto(r) for r in rows]
