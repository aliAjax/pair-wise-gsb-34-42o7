from fastapi import APIRouter, Depends
from src.controllers.inspection_result_controller import list_inspection_result, update_inspection_result
from src.middlewares.rbac_middleware import allow_roles

router = APIRouter(prefix="/api/inspection-result", tags=["InspectionResult"])
router.get("")(list_inspection_result)
# 检查项修改：仅巡检员，且只能改被退回点名的项
router.put("/{result_id}", dependencies=[Depends(allow_roles("INSPECTOR", "ADMIN"))])(update_inspection_result)
