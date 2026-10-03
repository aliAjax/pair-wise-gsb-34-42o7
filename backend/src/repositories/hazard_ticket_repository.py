from src.seed import seed
class HazardTicketRepository:
    def find_all(self):
        return seed["hazardTicket"]
