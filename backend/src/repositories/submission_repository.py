from src.seed import seed
class SubmissionRepository:
    """提交幂等登记表：同一 submission_id 重试直接返回首次处理结果。"""
    def __init__(self):
        self.rows = seed["submission"]
    def find_by_submission_id(self, submission_id):
        return next((row for row in self.rows if row["submission_id"] == submission_id), None)
    def save(self, row):
        existing = self.find_by_submission_id(row["submission_id"])
        if existing:
            return existing
        self.rows.append(row)
        return row
