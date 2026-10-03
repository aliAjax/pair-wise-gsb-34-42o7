from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.constructors.chain_dto_builder import build_result_dto
from src.constants.user_role import UserRole
from src.middlewares.auth_deps import CurrentUser, allow_roles
from src.repositories.inspection_result_repository import InspectionResultRepository

_reader = allow_roles(UserRole.INSPECTOR, UserRole.MAINTAINER, UserRole.SUPERVISOR, UserRole.AUDITOR)


def list_inspection_result(
    task_id: int | None = None,
    db: Session = Depends(get_db),
    _user: CurrentUser = Depends(_reader),
):
    rows = InspectionResultRepository(db).find_all(task_id)
    return [build_result_dto(r) for r in rows]
