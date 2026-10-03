from fastapi import APIRouter
from src.controllers.hazard_ticket_controller import list_hazard_ticket
router = APIRouter(prefix="/api/hazard-ticket", tags=["HazardTicket"])
router.get("")(list_hazard_ticket)
