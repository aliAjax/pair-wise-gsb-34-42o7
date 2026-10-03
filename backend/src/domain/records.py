"""复核链领域记录（dataclass）。FastAPI service 把 ORM 行转成这些对象后交给引擎。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TaskRecord:
    id: int
    building_id: int
    inspector_id: int
    plan_date: str
    task_type: str
    status: str
    checklist_version: str
    finished_at: str | None = None
    # 任务修订号：检查项修改/退回重开都会自增，提交必须携带其基于的修订号
    revision: int = 1
    checklist_items: list["ChecklistItemRecord"] = field(default_factory=list)


@dataclass
class ChecklistItemRecord:
    """检查项模板（任务的完整检查单内容）。"""

    item_code: str
    device_id: int
    title: str
    default_severity: str = "MEDIUM"
    active: bool = True


@dataclass
class ResultRecord:
    id: int
    task_id: int
    device_id: int
    item_code: str
    result_status: str  # PENDING / NORMAL / ABNORMAL
    measured_value: str = ""
    photo_url: str = ""
    note: str = ""
    review_state: str = "DRAFT"  # DRAFT/SUBMITTED/REVIEWED/RETURNED/DISCARDED
    severity_hint: str = "MEDIUM"
    revision: int = 1  # 该结果最近一次被写入时的任务修订号
    submitted_at: str | None = None
    reviewed_at: str | None = None
    returned_at: str | None = None


@dataclass
class HazardRecord:
    id: int
    result_id: int
    device_id: int
    task_id: int
    severity: str
    owner_id: int
    deadline: str
    rectify_status: str  # OPEN / RECTIFIED / CLOSED / CANCELLED
    rectify_note: str = ""
    closed_at: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    # 引擎内部字段：新结果尚未持久化时用于与结果配对（不直接落库）
    item_code: str | None = None


@dataclass
class DeviceRecord:
    id: int
    building_id: int
    device_code: str
    device_type: str
    floor: str
    location_desc: str
    install_date: str
    status: str  # 主数据状态 NORMAL/MAINTENANCE/RETIRED
    next_maintenance_at: str | None = None
    owner_id: int | None = None


@dataclass
class AuditEventRecord:
    id: int | None
    actor_id: int
    actor_role: str
    action: str
    target_type: str
    target_id: str
    detail: str = ""
    created_at: str = field(default_factory=utc_now_iso)


@dataclass
class ConflictRecord:
    """提交冲突区：旧修订/已复核的尝试一律落这里，绝不覆盖现结果。"""

    id: int | None
    task_id: int
    client_submission_id: str
    base_revision: int
    current_revision: int
    reason: str
    payload_preview: str
    created_at: str = field(default_factory=utc_now_iso)
