from src.repositories.inspection_task_repository import InspectionTaskRepository
class InspectionTaskService:
    def __init__(self):
        self.repo = InspectionTaskRepository()
    def list(self):
        return self.repo.find_all()
