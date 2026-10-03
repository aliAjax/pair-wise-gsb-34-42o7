from src.repositories.inspection_result_repository import InspectionResultRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.services.hazard_ticket_service import HazardTicketService
from src.services.fire_device_service import FireDeviceService
from src.services.audit_log_service import AuditLogService
from src.constants.inspection_status import TASK_FROZEN_STATUSES
from src.constants.review_state import EDITABLE_REVIEW_STATES
from src.constants.log_templates import LOG_TEMPLATES
from src.utils.errors import BusinessError

class InspectionResultService:
    """检查项修改：只放开被退回点名的项，改完重算隐患与设备状态。"""
    def __init__(self):
        self.repo = InspectionResultRepository()
        self.task_repo = InspectionTaskRepository()
        self.hazard_service = HazardTicketService()
        self.device_service = FireDeviceService()
        self.audit = AuditLogService()
    def list(self):
        return self.repo.find_all()
    def list_for_task(self, task_id):
        return self.repo.find_by_task(task_id)
    def update(self, result_id, payload, user):
        result = self.repo.find_by_id(result_id)
        if not result:
            raise BusinessError("NOT_FOUND", 404)
        task = self.task_repo.find_by_id(result["task_id"])
        if task and task["status"] in TASK_FROZEN_STATUSES:
            raise BusinessError("TASK_NOT_EDITABLE", 409)
        if result["review_state"] not in EDITABLE_REVIEW_STATES:
            raise BusinessError("RESULT_LOCKED", 409)
        for field in ("result_status", "measured_value", "photo_url", "note"):
            value = payload.get(field)
            if value is not None:
                result[field] = value
        self.repo.save(result)
        self.audit.record(LOG_TEMPLATES["InspectionResult"][1], user, "InspectionResult", result_id,
                          f"status={result['result_status']}")
        # 隐患与设备状态随检查项修改重算
        self.hazard_service.sync_for_result(result, payload.get("severity", "MEDIUM"),
                                            result.get("submission_id") or f"manual-{result_id}",
                                            self.audit, user)
        device = self.device_service.recompute(result["device_id"], self.audit, user)
        return {"result": result, "device": device}
