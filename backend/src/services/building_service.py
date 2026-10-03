from src.repositories.building_repository import BuildingRepository
class BuildingService:
    def __init__(self):
        self.repo = BuildingRepository()
    def list(self):
        return self.repo.find_all()
