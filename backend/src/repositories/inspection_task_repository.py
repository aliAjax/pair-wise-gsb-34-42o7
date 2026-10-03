from sqlalchemy import select

from src.models.inspection_task import InspectionTask


class InspectionTaskRepository:
    def __init__(self, db=None):
        self.db = db

    def find_all(self, building_id: int | None = None, inspector_id: int | None = None):
        if self.db is None:
            return []
        stmt = select(InspectionTask)
        if building_id is not None:
            stmt = stmt.where(InspectionTask.building_id == building_id)
        if inspector_id is not None:
            stmt = stmt.where(InspectionTask.inspector_id == inspector_id)
        return list(self.db.scalars(stmt).all())

    def get(self, task_id: int):
        return self.db.get(InspectionTask, task_id) if self.db else None

    def create(self, data: dict) -> InspectionTask:
        row = InspectionTask(**data)
        self.db.add(row)
        self.db.flush()
        return row
