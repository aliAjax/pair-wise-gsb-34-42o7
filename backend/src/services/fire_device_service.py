from src.repositories.fire_device_repository import FireDeviceRepository
class FireDeviceService:
    def __init__(self):
        self.repo = FireDeviceRepository()
    def list(self):
        return self.repo.find_all()
