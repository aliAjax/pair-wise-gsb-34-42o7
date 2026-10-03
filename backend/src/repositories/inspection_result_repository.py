from src.seed import seed
class InspectionResultRepository:
    def __init__(self):
        self.rows = seed["inspectionResult"]
    def find_all(self):
        return list(self.rows)
    def find_by_id(self, result_id):
        return next((row for row in self.rows if row["id"] == result_id), None)
    def find_by_task(self, task_id):
        return [row for row in self.rows if row["task_id"] == task_id]
    def find_by_task_item(self, task_id, item_code):
        return next((row for row in self.rows if row["task_id"] == task_id and row["item_code"] == item_code), None)
    def next_id(self):
        return max((row["id"] for row in self.rows), default=0) + 1
    def save(self, row):
        existing = self.find_by_id(row["id"])
        if existing:
            existing.update(row)
            return existing
        self.rows.append(row)
        return row
