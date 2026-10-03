from fastapi import APIRouter
from src.controllers.building_controller import list_building
router = APIRouter(prefix="/api/building", tags=["Building"])
router.get("")(list_building)
