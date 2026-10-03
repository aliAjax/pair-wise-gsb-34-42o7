from fastapi import APIRouter

from src.controllers.fire_device_controller import (
    device_history_controller,
    list_devices_controller,
)

router = APIRouter(prefix="/api/devices", tags=["FireDevice"])

router.get("")(list_devices_controller)
router.get("/{device_id}/history")(device_history_controller)
