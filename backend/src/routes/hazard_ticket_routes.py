from fastapi import APIRouter

from src.controllers.hazard_ticket_controller import (
    assign_hazard_controller,
    list_hazards_controller,
    rectify_hazard_controller,
    verify_hazard_controller,
)

router = APIRouter(prefix="/api/hazards", tags=["HazardTicket"])

router.get("")(list_hazards_controller)
router.post("/{hazard_id}/assign")(assign_hazard_controller)
# 维保商处理隐患
router.post("/{hazard_id}/rectify")(rectify_hazard_controller)
# 物业主管复验关闭 / 复验退回
router.post("/{hazard_id}/verify")(verify_hazard_controller)
