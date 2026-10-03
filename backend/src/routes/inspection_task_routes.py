from fastapi import APIRouter, Depends
from src.controllers.inspection_task_controller import (
    list_inspection_task, get_inspection_task, list_inspection_task_conflicts,
    submit_inspection_task, review_inspection_task, reject_inspection_task
)
from src.middlewares.rbac_middleware import allow_roles

router = APIRouter(prefix="/api/inspection-task", tags=["InspectionTask"])
router.get("")(list_inspection_task)
router.get("/{task_id}")(get_inspection_task)
router.get("/{task_id}/conflicts")(list_inspection_task_conflicts)
# 提交/重提交：巡检员；复核与退回：审计员，权限隔离
router.post("/{task_id}/submit", dependencies=[Depends(allow_roles("INSPECTOR", "ADMIN"))])(submit_inspection_task)
router.post("/{task_id}/review", dependencies=[Depends(allow_roles("AUDITOR", "ADMIN"))])(review_inspection_task)
router.post("/{task_id}/reject", dependencies=[Depends(allow_roles("AUDITOR", "ADMIN"))])(reject_inspection_task)
