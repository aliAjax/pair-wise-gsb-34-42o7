from pydantic import BaseModel
class AuditLog(BaseModel):
    id: int | float
    actor: int | float
    role: str
    action: str
    entity: str
    entity_id: int | float
    detail: str
    created_at: str
