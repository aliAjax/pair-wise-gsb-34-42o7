from sqlalchemy import select

from src.models.hazard_ticket import HazardTicket


class HazardTicketRepository:
    def __init__(self, db=None):
        self.db = db

    def find_all(self, device_id: int | None = None, rectify_status: str | None = None):
        if self.db is None:
            return []
        stmt = select(HazardTicket)
        if device_id is not None:
            stmt = stmt.where(HazardTicket.device_id == device_id)
        if rectify_status is not None:
            stmt = stmt.where(HazardTicket.rectify_status == rectify_status)
        return list(self.db.scalars(stmt).all())
