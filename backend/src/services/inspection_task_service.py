from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.repositories.conflict_entry_repository import ConflictEntryRepository
from src.repositories.submission_repository import SubmissionRepository
from src.services.hazard_ticket_service import HazardTicketService
from src.services.fire_device_service import FireDeviceService
from src.services.audit_log_service import AuditLogService
from src.constants.inspection_status import TASK_SUBMITTABLE_STATUSES
from src.constants.review_state import EDITABLE_REVIEW_STATES
from src.constants.log_templates import LOG_TEMPLATES
from src.utils.errors import BusinessError
from src.utils.formatters import now_iso

class InspectionTaskService:
    """复核链：提交带修订号，旧修订进冲突区；复核退回只放开被点名的检查项。"""
    def __init__(self):
        self.repo = InspectionTaskRepository()
        self.result_repo = InspectionResultRepository()
        self.conflict_repo = ConflictEntryRepository()
        self.submission_repo = SubmissionRepository()
        self.hazard_service = HazardTicketService()
        self.device_service = FireDeviceService()
        self.audit = AuditLogService()
    def list(self):
        return self.repo.find_all()
    def get(self, task_id):
        task = self.repo.find_by_id(task_id)
        if not task:
            raise BusinessError("NOT_FOUND", 404)
        return task
    def list_conflicts(self, task_id):
        self.get(task_id)
        return self.conflict_repo.find_by_task(task_id)
    def submit(self, task_id, payload, user):
        task = self.get(task_id)
        submission_id = payload["submission_id"]
        # 幂等：同一提交（含断网重试）直接返回首次处理结果，不重复生成隐患单
        replay = self.submission_repo.find_by_submission_id(submission_id)
        if replay:
            return {**replay["response"], "replayed": True}
        # 修订号校验：旧修订留在冲突区，不能覆盖已复核结果
        if payload["revision"] != task["revision"]:
            self.conflict_repo.save({
                "id": self.conflict_repo.next_id(),
                "task_id": task_id,
                "submission_id": submission_id,
                "revision": payload["revision"],
                "current_revision": task["revision"],
                "payload": payload,
                "reason": "REVISION_CONFLICT",
                "created_at": now_iso()
            })
            self.audit.record(LOG_TEMPLATES["InspectionTask"][7], user, "InspectionTask", task_id,
                              f"revision={payload['revision']} current={task['revision']}")
            raise BusinessError("REVISION_CONFLICT", 409)
        if task["status"] not in TASK_SUBMITTABLE_STATUSES:
            raise BusinessError("TASK_NOT_EDITABLE", 409)
        applied, skipped = [], []
        for item in payload["results"]:
            existing = self.result_repo.find_by_task_item(task_id, item["item_code"])
            if existing and existing["review_state"] not in EDITABLE_REVIEW_STATES:
                # 已提交/已复核的检查项保持原状，整包重投也不覆盖
                skipped.append(existing["item_code"])
                continue
            row = existing or {
                "id": self.result_repo.next_id(),
                "task_id": task_id,
                "device_id": item["device_id"],
                "item_code": item["item_code"]
            }
            row.update({
                "device_id": item["device_id"],
                "result_status": item["result_status"],
                "measured_value": item.get("measured_value", ""),
                "photo_url": item.get("photo_url", ""),
                "note": item.get("note", ""),
                "submission_id": submission_id,
                "task_revision": task["revision"],
                "review_state": "SUBMITTED"
            })
            self.result_repo.save(row)
            applied.append(row)
        severity_by_item = {item["item_code"]: item.get("severity") or "MEDIUM"
                            for item in payload["results"]}
        hazards = []
        for row in applied:
            if row["result_status"] == "ABNORMAL":
                hazards.append(self.hazard_service.ensure_for_result(
                    row, severity_by_item.get(row["item_code"], "MEDIUM"),
                    submission_id, self.audit, user))
        device_ids = sorted({row["device_id"] for row in applied})
        devices = [self.device_service.recompute(device_id, self.audit, user) for device_id in device_ids]
        task["status"] = "SUBMITTED"
        task["finished_at"] = now_iso()
        self.repo.save(task)
        self.audit.record(LOG_TEMPLATES["InspectionTask"][4], user, "InspectionTask", task_id,
                          f"submission={submission_id} applied={len(applied)} skipped={len(skipped)}")
        response = {"task": task, "results": applied, "skipped_items": skipped,
                    "hazards": hazards, "devices": devices, "replayed": False}
        self.submission_repo.save({"submission_id": submission_id, "task_id": task_id,
                                   "revision": task["revision"], "response": response,
                                   "created_at": now_iso()})
        return response
    def review(self, task_id, user):
        task = self.get(task_id)
        if task["status"] != "SUBMITTED":
            raise BusinessError("TASK_NOT_EDITABLE", 409)
        for row in self.result_repo.find_by_task(task_id):
            row["review_state"] = "REVIEWED"
            self.result_repo.save(row)
        task["status"] = "REVIEWED"
        task["revision"] += 1
        self.repo.save(task)
        self.audit.record(LOG_TEMPLATES["InspectionTask"][5], user, "InspectionTask", task_id,
                          f"revision -> {task['revision']}")
        return task
    def reject(self, task_id, item_codes, note, user):
        task = self.get(task_id)
        if task["status"] != "SUBMITTED":
            raise BusinessError("TASK_NOT_EDITABLE", 409)
        reopened = []
        for row in self.result_repo.find_by_task(task_id):
            if row["item_code"] in item_codes:
                row["review_state"] = "REOPENED"
                self.result_repo.save(row)
                reopened.append(row["item_code"])
                self.audit.record(LOG_TEMPLATES["InspectionResult"][4], user, "InspectionResult", row["id"],
                                  f"item={row['item_code']}")
        # 未被点名的检查项保持原状
        task["status"] = "IN_PROGRESS"
        task["revision"] += 1
        self.repo.save(task)
        self.audit.record(LOG_TEMPLATES["InspectionTask"][6], user, "InspectionTask", task_id,
                          f"reopened={','.join(reopened)} note={note}")
        return {"task": task, "reopened_items": reopened}
