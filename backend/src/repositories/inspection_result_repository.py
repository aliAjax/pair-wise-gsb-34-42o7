from sqlalchemy import select

from src.models.inspection_result import InspectionResult


class InspectionResultRepository:
    def __init__(self, db=None):
        self.db = db

    def find_all(self, task_id: int | None = None):
        if self.db is None:
            return []
        stmt = select(InspectionResult)
        if task_id is not None:
            stmt = stmt.where(InspectionResult.task_id == task_id)
        return list(self.db.scalars(stmt).all())
