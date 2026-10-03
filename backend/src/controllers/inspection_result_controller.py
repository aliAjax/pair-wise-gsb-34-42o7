from fastapi import HTTPException, Request
from src.services.inspection_result_service import InspectionResultService
from src.middlewares.error_handler_middleware import to_error_payload
from src.types.inspection_result_payload import UpdateResultPayload
from src.utils.errors import BusinessError

service = InspectionResultService()

def list_inspection_result(task_id: int | None = None):
    rows = service.list()
    if task_id is not None:
        rows = [row for row in rows if row["task_id"] == task_id]
    return rows

def update_inspection_result(result_id: int, payload: UpdateResultPayload, request: Request):
    try:
        return service.update(result_id, payload.model_dump(), request.state.user)
    except BusinessError as exc:
        raise HTTPException(status_code=exc.status, detail=to_error_payload(exc))
