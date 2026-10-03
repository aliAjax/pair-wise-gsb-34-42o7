from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.constants.user_role import UserRole
from src.middlewares.auth_deps import CurrentUser, allow_roles
from src.repositories.building_repository import BuildingRepository

_reader = allow_roles(UserRole.INSPECTOR, UserRole.MAINTAINER, UserRole.SUPERVISOR, UserRole.AUDITOR)


def list_building(
    db: Session = Depends(get_db),
    _user: CurrentUser = Depends(_reader),
):
    rows = BuildingRepository(db).find_all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "campus": r.campus,
            "floor_count": r.floor_count,
            "fire_grade": r.fire_grade,
            "manager_id": r.manager_id,
            "address_code": r.address_code,
        }
        for r in rows
    ]
