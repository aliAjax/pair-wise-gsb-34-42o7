from sqlalchemy import select

from src.models.fire_device import FireDevice


class FireDeviceRepository:
    def __init__(self, db=None):
        self.db = db

    def find_all(self, building_id: int | None = None):
        if self.db is None:
            return []
        stmt = select(FireDevice)
        if building_id is not None:
            stmt = stmt.where(FireDevice.building_id == building_id)
        return list(self.db.scalars(stmt).all())

    def get(self, device_id: int):
        return self.db.get(FireDevice, device_id) if self.db else None

    def create(self, data: dict) -> FireDevice:
        row = FireDevice(**data)
        self.db.add(row)
        self.db.flush()
        return row
