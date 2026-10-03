"""隐患 controller：列表、派单、整改、复验关闭。"""

from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.constants.user_role import UserRole
from src.middlewares.auth_deps import CurrentUser, allow_roles
from src.services.hazard_app_service import HazardAppService
from src.types.chain_payloads import AssignHazardPayload, RectifyHazardPayload, VerifyHazardPayload

_reader = allow_roles(UserRole.INSPECTOR, UserRole.MAINTAINER, UserRole.SUPERVISOR, UserRole.AUDITOR)


def list_hazards_controller(
    status: str | None = None,
    device_id: int | None = None,
    db: Session = Depends(get_db),
    _user: CurrentUser = Depends(_reader),
):
    return HazardAppService(db).list_hazards(status, device_id)


def assign_hazard_controller(
    hazard_id: int,
    payload: AssignHazardPayload,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(allow_roles(UserRole.SUPERVISOR)),
):
    return HazardAppService(db).assign(hazard_id, payload.owner_id, user.id, user.role)


def rectify_hazard_controller(
    hazard_id: int,
    payload: RectifyHazardPayload,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(allow_roles(UserRole.MAINTAINER)),
):
    return HazardAppService(db).rectify(hazard_id, payload.rectify_note, user.id, user.role)


def verify_hazard_controller(
    hazard_id: int,
    payload: VerifyHazardPayload,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(allow_roles(UserRole.SUPERVISOR)),
):
    return HazardAppService(db).verify(hazard_id, payload.approved, payload.note, user.id, user.role)
