from fastapi import APIRouter
from src.controllers.fire_device_controller import list_fire_device
router = APIRouter(prefix="/api/fire-device", tags=["FireDevice"])
router.get("")(list_fire_device)
