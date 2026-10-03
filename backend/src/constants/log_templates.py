"""日志模板集中点：字段变更时必须同步修改这里与所有调用处。"""

LOG_TEMPLATES = {
    "Building": [
        "Building.create",
        "Building.update",
        "Building.status",
        "Building.export",
    ],
    "FireDevice": [
        "FireDevice.create",
        "FireDevice.update",
        "FireDevice.status",
        "FireDevice.export",
        "FireDevice.recompute_compliance",
    ],
    "InspectionTask": [
        "InspectionTask.create",
        "InspectionTask.update",
        "InspectionTask.status",
        "InspectionTask.export",
        "InspectionTask.submit",
        "InspectionTask.reopen_full",
        "InspectionTask.checklist_change",
        "InspectionTask.revision_bump",
    ],
    "InspectionResult": [
        "InspectionResult.create",
        "InspectionResult.update",
        "InspectionResult.status",
        "InspectionResult.export",
        "InspectionResult.review_approve",
        "InspectionResult.review_return",
        "InspectionResult.discard",
    ],
    "HazardTicket": [
        "HazardTicket.create",
        "HazardTicket.update",
        "HazardTicket.status",
        "HazardTicket.export",
        "HazardTicket.rectify",
        "HazardTicket.verify_close",
        "HazardTicket.auto_cancel",
    ],
    "Submission": [
        "Submission.accept",
        "Submission.partial",
        "Submission.conflict",
        "Submission.replay_idempotent",
    ],
    "Auth": ["Auth.login", "Auth.denied"],
}


class AuditAction:
    TASK_CREATE = "InspectionTask.create"
    TASK_SUBMIT = "InspectionTask.submit"
    TASK_REOPEN = "InspectionTask.reopen_full"
    TASK_CHECKLIST_CHANGE = "InspectionTask.checklist_change"
    TASK_REVISION_BUMP = "InspectionTask.revision_bump"
    RESULT_UPDATE = "InspectionResult.update"
    RESULT_REVIEW_APPROVE = "InspectionResult.review_approve"
    RESULT_REVIEW_RETURN = "InspectionResult.review_return"
    RESULT_DISCARD = "InspectionResult.discard"
    HAZARD_CREATE = "HazardTicket.create"
    HAZARD_RECTIFY = "HazardTicket.rectify"
    HAZARD_VERIFY_CLOSE = "HazardTicket.verify_close"
    HAZARD_AUTO_CANCEL = "HazardTicket.auto_cancel"
    DEVICE_RECOMPUTE = "FireDevice.recompute_compliance"
    SUBMISSION_ACCEPT = "Submission.accept"
    SUBMISSION_PARTIAL = "Submission.partial"
    SUBMISSION_CONFLICT = "Submission.conflict"
    SUBMISSION_REPLAY = "Submission.replay_idempotent"
    AUTH_LOGIN = "Auth.login"
    AUTH_DENIED = "Auth.denied"
