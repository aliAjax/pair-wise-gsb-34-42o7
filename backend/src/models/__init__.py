"""SQLAlchemy 2.0 ORM 模型汇总。"""

from src.models.audit_log import AuditLog
from src.models.building import Building
from src.models.fire_device import FireDevice
from src.models.hazard_ticket import HazardTicket
from src.models.inspection_result import InspectionResult
from src.models.inspection_task import InspectionTask
from src.models.submission_conflict import SubmissionConflict
from src.models.submission_record import SubmissionRecord
from src.models.user_account import UserAccount

__all__ = [
    "AuditLog",
    "Building",
    "FireDevice",
    "HazardTicket",
    "InspectionResult",
    "InspectionTask",
    "SubmissionConflict",
    "SubmissionRecord",
    "UserAccount",
]
