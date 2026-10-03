from src.repositories.inspection_result_repository import InspectionResultRepository
class InspectionResultService:
    def __init__(self):
        self.repo = InspectionResultRepository()
    def list(self):
        return self.repo.find_all()
