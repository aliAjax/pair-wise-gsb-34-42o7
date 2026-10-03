from src.seed import seed
class FireDeviceRepository:
    def __init__(self):
        self.rows = seed["fireDevice"]
    def find_all(self):
        return list(self.rows)
    def find_by_id(self, device_id):
        return next((row for row in self.rows if row["id"] == device_id), None)
    def save(self, row):
        existing = self.find_by_id(row["id"])
        if existing:
            existing.update(row)
            return existing
        self.rows.append(row)
        return row
