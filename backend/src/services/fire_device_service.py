"""消防设备服务入口；台账展示请使用 FireDeviceAppService（含合规重算）。"""

from src.repositories.fire_device_repository import FireDeviceRepository
from src.services.fire_device_app_service import FireDeviceAppService


class FireDeviceService:
    def __init__(self, db=None):
        self.repo = FireDeviceRepository(db)

    def list(self):
        return self.repo.find_all()
