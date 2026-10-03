from fastapi import APIRouter

from src.controllers.inspection_task_controller import (
    change_checklist_controller,
    create_task_controller,
    get_full_task_controller,
    list_conflicts_controller,
    list_task_results_controller,
    list_tasks_controller,
    review_task_controller,
    submit_task_controller,
)

router = APIRouter(prefix="/api/inspection-tasks", tags=["InspectionTask"])

router.get("")(list_tasks_controller)
# 静态路径必须在 {task_id} 之前注册，避免 "conflicts" 被当成任务 id
router.get("/conflicts/zone")(list_conflicts_controller)
router.post("")(create_task_controller)
router.get("/{task_id}/full")(get_full_task_controller)
router.get("/{task_id}/results")(list_task_results_controller)
# 断网恢复后从完整任务继续提交（携带 base_revision + client_submission_id）
router.post("/{task_id}/submissions")(submit_task_controller)
# 物业主管复核（APPROVE/RETURN，RETURN 只放开被点名检查项）
router.post("/{task_id}/reviews")(review_task_controller)
# 检查项增删改：修订号自增，隐患与设备状态重算
router.patch("/{task_id}/checklist")(change_checklist_controller)
