from fastapi import HTTPException, Request
from src.services.inspection_task_service import InspectionTaskService
from src.middlewares.error_handler_middleware import to_error_payload
from src.types.inspection_task_payload import SubmitTaskPayload, RejectTaskPayload
from src.utils.errors import BusinessError

service = InspectionTaskService()

def list_inspection_task():
    return service.list()

def get_inspection_task(task_id: int):
    try:
        return service.get(task_id)
    except BusinessError as exc:
        raise HTTPException(status_code=exc.status, detail=to_error_payload(exc))

def list_inspection_task_conflicts(task_id: int):
    try:
        return service.list_conflicts(task_id)
    except BusinessError as exc:
        raise HTTPException(status_code=exc.status, detail=to_error_payload(exc))

def submit_inspection_task(task_id: int, payload: SubmitTaskPayload, request: Request):
    try:
        return service.submit(task_id, payload.model_dump(), request.state.user)
    except BusinessError as exc:
        raise HTTPException(status_code=exc.status, detail=to_error_payload(exc))

def review_inspection_task(task_id: int, request: Request):
    try:
        return service.review(task_id, request.state.user)
    except BusinessError as exc:
        raise HTTPException(status_code=exc.status, detail=to_error_payload(exc))

def reject_inspection_task(task_id: int, payload: RejectTaskPayload, request: Request):
    try:
        return service.reject(task_id, payload.item_codes, payload.note, request.state.user)
    except BusinessError as exc:
        raise HTTPException(status_code=exc.status, detail=to_error_payload(exc))
