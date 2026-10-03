from src.repositories.audit_log_repository import AuditLogRepository
from src.utils.formatters import now_iso

class AuditLogService:
    """复核链审计：提交/复核/退回/关单/状态重算全部留痕，重开后仍可追溯。"""
    def __init__(self):
        self.repo = AuditLogRepository()
    def record(self, template, actor, entity, entity_id, detail=""):
        row = {
            "id": self.repo.next_id(),
            "actor": actor.get("id", 0) if isinstance(actor, dict) else 0,
            "role": actor.get("role", "SYSTEM") if isinstance(actor, dict) else "SYSTEM",
            "action": template,
            "entity": entity,
            "entity_id": entity_id,
            "detail": detail,
            "created_at": now_iso()
        }
        return self.repo.save(row)
    def list(self):
        return self.repo.find_all()
    def list_for_entity(self, entity, entity_id):
        return self.repo.find_by_entity(entity, entity_id)
