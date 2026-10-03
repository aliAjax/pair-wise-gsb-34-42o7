from fastapi import APIRouter
from src.controllers.inspection_result_controller import list_inspection_result
router = APIRouter(prefix="/api/inspection-result", tags=["InspectionResult"])
router.get("")(list_inspection_result)
