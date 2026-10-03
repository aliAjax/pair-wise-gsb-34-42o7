"""巡检任务 controller：列表、建档、完整任务、提交、复核、检查项修改。"""

from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.middlewares.auth_deps import CurrentUser, allow_roles, get_current_user
from src.constants.user_role import UserRole
from src.services.chain_service import ChainService
from src.services.inspection_task_app_service import InspectionTaskAppService
from src.types.chain_payloads import (
    ChecklistChangePayload,
    ReviewPayload,
    SubmitTaskPayload,
    TaskCreatePayload,
)

_reader = allow_roles(UserRole.INSPECTOR, UserRole.MAINTAINER, UserRole.SUPERVISOR, UserRole.AUDITOR)


def list_tasks_controller(
    building_id: int | None = None,
    inspector_id: int | None = None,
    db: Session = Depends(get_db),
    _user: CurrentUser = Depends(_reader),
):
    return InspectionTaskAppService(db).list_tasks(building_id, inspector_id)


def create_task_controller(
    payload: TaskCreatePayload,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(allow_roles(UserRole.SUPERVISOR)),
):
    return InspectionTaskAppService(db).create_task(payload, user.id)


def get_full_task_controller(
    task_id: int,
    db: Session = Depends(get_db),
    _user: CurrentUser = Depends(_reader),
):
    # 断网恢复后从这里拉取“完整任务”（含修订号与全量检查项）
    return InspectionTaskAppService(db).full_task(task_id)


def list_task_results_controller(
    task_id: int,
    db: Session = Depends(get_db),
    _user: CurrentUser = Depends(_reader),
):
    return InspectionTaskAppService(db).task_results(task_id)


def submit_task_controller(
    task_id: int,
    payload: SubmitTaskPayload,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(allow_roles(UserRole.INSPECTOR)),
):
    # 提交带任务修订号；同一 client_submission_id 重试由 service 幂等回放
    return ChainService(db).submit_full_task(
        task_id, payload.model_dump(), user.id, user.role,
    )


def review_task_controller(
    task_id: int,
    payload: ReviewPayload,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(allow_roles(UserRole.SUPERVISOR)),
):
    return ChainService(db).review(task_id, payload.model_dump(), user.id, user.role)


def change_checklist_controller(
    task_id: int,
    payload: ChecklistChangePayload,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(allow_roles(UserRole.SUPERVISOR)),
):
    return ChainService(db).change_checklist(task_id, payload.model_dump(), user.id, user.role)


def list_conflicts_controller(
    task_id: int | None = None,
    db: Session = Depends(get_db),
    _user: CurrentUser = Depends(
        allow_roles(UserRole.SUPERVISOR, UserRole.INSPECTOR, UserRole.AUDITOR)
    ),
):
    from src.constructors.chain_dto_builder import build_conflict_dto

    rows = ChainService(db).conflicts(task_id)
    return [build_conflict_dto(r) for r in rows]
