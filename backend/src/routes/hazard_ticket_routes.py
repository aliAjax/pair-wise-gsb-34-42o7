from fastapi import APIRouter, Depends
from src.controllers.hazard_ticket_controller import list_hazard_ticket, close_hazard_ticket
from src.middlewares.rbac_middleware import allow_roles

router = APIRouter(prefix="/api/hazard-ticket", tags=["HazardTicket"])
router.get("")(list_hazard_ticket)
# 隐患整改关单：仅维保商
router.post("/{ticket_id}/close", dependencies=[Depends(allow_roles("MAINTAINER", "ADMIN"))])(close_hazard_ticket)
