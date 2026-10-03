"""巡检任务服务入口；复核链操作请使用 InspectionTaskAppService / ChainService。"""

from src.repositories.inspection_task_repository import InspectionTaskRepository


class InspectionTaskService:
    def __init__(self, db=None):
        self.repo = InspectionTaskRepository(db)

    def list(self):
        return self.repo.find_all()
