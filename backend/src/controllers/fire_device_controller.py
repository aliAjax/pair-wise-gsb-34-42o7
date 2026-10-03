"""消防设备 controller：台账（合规状态重算）与设备历史。"""

from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.constants.user_role import UserRole
from src.middlewares.auth_deps import CurrentUser, allow_roles
from src.services.fire_device_app_service import FireDeviceAppService

_reader = allow_roles(UserRole.INSPECTOR, UserRole.MAINTAINER, UserRole.SUPERVISOR, UserRole.AUDITOR)


def list_devices_controller(
    building_id: int | None = None,
    floor: str | None = None,
    db: Session = Depends(get_db),
    _user: CurrentUser = Depends(_reader),
):
    return FireDeviceAppService(db).list_devices(building_id, floor)


def device_history_controller(
    device_id: int,
    db: Session = Depends(get_db),
    _user: CurrentUser = Depends(_reader),
):
    return FireDeviceAppService(db).device_history(device_id)
