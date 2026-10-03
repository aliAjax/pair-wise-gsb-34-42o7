from sqlalchemy import select

from src.models.building import Building


class BuildingRepository:
    def __init__(self, db=None):
        self.db = db

    def find_all(self):
        if self.db is None:
            return []
        return list(self.db.scalars(select(Building)).all())

    def get(self, building_id: int):
        return self.db.get(Building, building_id) if self.db else None

    def create(self, data: dict) -> Building:
        row = Building(**data)
        self.db.add(row)
        self.db.flush()
        return row
