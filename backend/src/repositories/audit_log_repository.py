from src.seed import seed
class AuditLogRepository:
    def __init__(self):
        self.rows = seed["auditLog"]
    def find_all(self):
        return list(self.rows)
    def find_by_entity(self, entity, entity_id):
        return [row for row in self.rows if row["entity"] == entity and row["entity_id"] == entity_id]
    def next_id(self):
        return max((row["id"] for row in self.rows), default=0) + 1
    def save(self, row):
        self.rows.append(row)
        return row
