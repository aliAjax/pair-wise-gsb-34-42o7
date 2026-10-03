from src.services.audit_log_service import AuditLogService
service = AuditLogService()
def list_audit_log(entity: str | None = None, entity_id: int | None = None):
    if entity and entity_id is not None:
        return service.list_for_entity(entity, entity_id)
    return service.list()
