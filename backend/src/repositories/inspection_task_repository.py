from src.seed import seed
class InspectionTaskRepository:
    def find_all(self):
        return seed["inspectionTask"]
