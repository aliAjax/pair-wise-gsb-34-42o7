"""隐患整改服务：列表、派单、整改、复验。"""

from sqlalchemy.orm import Session

from src.constructors.chain_dto_builder import build_hazard_dto
from src.models.hazard_ticket import HazardTicket
from src.services.chain_service import ChainService


class HazardAppService:
    def __init__(self, db: Session):
        self.db = db

    def list_hazards(self, status: str | None = None, device_id: int | None = None):
        query = self.db.query(HazardTicket)
        if status:
            query = query.filter(HazardTicket.rectify_status == status)
        if device_id is not None:
            query = query.filter(HazardTicket.device_id == device_id)
        rows = query.order_by(HazardTicket.id.desc()).all()
        return [build_hazard_dto(r) for r in rows]

    def assign(self, hazard_id: int, owner_id: int, actor_id: int, actor_role: str):
        row = ChainService(self.db).assign_hazard(hazard_id, owner_id, actor_id, actor_role)
        return build_hazard_dto(row)

    def rectify(self, hazard_id: int, note: str, actor_id: int, actor_role: str):
        row = ChainService(self.db).rectify_hazard(hazard_id, note, actor_id, actor_role)
        return build_hazard_dto(row)

    def verify(self, hazard_id: int, approved: bool, note: str, actor_id: int, actor_role: str):
        row = ChainService(self.db).verify_hazard(hazard_id, approved, note, actor_id, actor_role)
        return build_hazard_dto(row)
