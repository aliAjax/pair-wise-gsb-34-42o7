from src.seed import seed
class ConflictEntryRepository:
    """冲突区：修订号过期的提交留档，永不写回正式结果。"""
    def __init__(self):
        self.rows = seed["conflictEntry"]
    def find_all(self):
        return list(self.rows)
    def find_by_task(self, task_id):
        return [row for row in self.rows if row["task_id"] == task_id]
    def next_id(self):
        return max((row["id"] for row in self.rows), default=0) + 1
    def save(self, row):
        self.rows.append(row)
        return row
