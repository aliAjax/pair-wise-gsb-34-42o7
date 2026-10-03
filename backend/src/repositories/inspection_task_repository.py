from src.seed import seed
class InspectionTaskRepository:
    def __init__(self):
        self.rows = seed["inspectionTask"]
    def find_all(self):
        return list(self.rows)
    def find_by_id(self, task_id):
        return next((row for row in self.rows if row["id"] == task_id), None)
    def save(self, row):
        existing = self.find_by_id(row["id"])
        if existing:
            existing.update(row)
            return existing
        self.rows.append(row)
        return row
