from src.repositories.hazard_ticket_repository import HazardTicketRepository
class HazardTicketService:
    def __init__(self):
        self.repo = HazardTicketRepository()
    def list(self):
        return self.repo.find_all()
