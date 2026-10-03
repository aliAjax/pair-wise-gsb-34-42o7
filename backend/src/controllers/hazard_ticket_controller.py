from fastapi import HTTPException, Request
from src.services.hazard_ticket_service import HazardTicketService
from src.services.fire_device_service import FireDeviceService
from src.services.audit_log_service import AuditLogService
from src.middlewares.error_handler_middleware import to_error_payload
from src.types.hazard_ticket_payload import CloseHazardPayload
from src.utils.errors import BusinessError

service = HazardTicketService()
device_service = FireDeviceService()
audit = AuditLogService()

def list_hazard_ticket():
    return service.list()

def close_hazard_ticket(ticket_id: int, payload: CloseHazardPayload, request: Request):
    try:
        ticket = service.close(ticket_id, payload.rectify_note, audit, request.state.user)
        # 关单后重算设备台账状态
        device = device_service.recompute(ticket["device_id"], audit, request.state.user)
        return {"ticket": ticket, "device": device}
    except BusinessError as exc:
        raise HTTPException(status_code=exc.status, detail=to_error_payload(exc))
