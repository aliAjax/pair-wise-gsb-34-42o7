from src.services.building_service import BuildingService
service = BuildingService()
def list_building():
    return service.list()
