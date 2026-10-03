"""楼栋服务（薄封装，业务写动作在复核链相关服务中）。"""

from src.repositories.building_repository import BuildingRepository


class BuildingService:
    def __init__(self, db=None):
        self.repo = BuildingRepository(db)

    def list(self):
        return self.repo.find_all()
