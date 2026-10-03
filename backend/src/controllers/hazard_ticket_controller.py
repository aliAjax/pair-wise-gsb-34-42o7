from src.services.hazard_ticket_service import HazardTicketService
service = HazardTicketService()
def list_hazard_ticket():
    return service.list()
