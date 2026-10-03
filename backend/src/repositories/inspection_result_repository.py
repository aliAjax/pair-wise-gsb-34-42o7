from src.seed import seed
class InspectionResultRepository:
    def find_all(self):
        return seed["inspectionResult"]
