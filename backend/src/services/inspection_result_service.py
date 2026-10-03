"""巡检结果服务入口；提交/复核由 ChainService 处理。"""

from src.repositories.inspection_result_repository import InspectionResultRepository


class InspectionResultService:
    def __init__(self, db=None):
        self.repo = InspectionResultRepository(db)

    def list(self, task_id: int | None = None):
        return self.repo.find_all(task_id)
