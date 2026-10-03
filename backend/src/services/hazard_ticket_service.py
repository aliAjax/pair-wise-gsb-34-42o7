"""隐患服务入口；整改链操作请使用 HazardAppService。"""

from src.repositories.hazard_ticket_repository import HazardTicketRepository


class HazardTicketService:
    def __init__(self, db=None):
        self.repo = HazardTicketRepository(db)

    def list(self):
        return self.repo.find_all()
