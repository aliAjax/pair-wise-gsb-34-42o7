from src.services.fire_device_service import FireDeviceService
service = FireDeviceService()
def list_fire_device():
    return service.list()
