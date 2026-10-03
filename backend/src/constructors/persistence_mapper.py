"""ORM 行 ↔ 复核链领域记录 的映射器（持久化与纯逻辑解耦）。"""

from __future__ import annotations

from src.domain.records import (
    ChecklistItemRecord,
    DeviceRecord,
    HazardRecord,
    ResultRecord,
    TaskRecord,
)


def orm_to_task(row) -> TaskRecord:
    items = [
        ChecklistItemRecord(
            item_code=item["item_code"],
            device_id=item["device_id"],
            title=item.get("title", ""),
            default_severity=item.get("default_severity", "MEDIUM"),
            active=item.get("active", True),
        )
        for item in (row.checklist_items or [])
    ]
    return TaskRecord(
        id=row.id,
        building_id=row.building_id,
        inspector_id=row.inspector_id,
        plan_date=row.plan_date,
        task_type=row.task_type,
        status=row.status,
        checklist_version=row.checklist_version,
        finished_at=row.finished_at,
        revision=row.revision,
        checklist_items=items,
    )


def apply_task_to_orm(task: TaskRecord, row) -> None:
    row.status = task.status
    row.revision = task.revision
    row.checklist_version = task.checklist_version
    row.finished_at = task.finished_at
    row.checklist_items = [
        {
            "item_code": item.item_code,
            "device_id": item.device_id,
            "title": item.title,
            "default_severity": item.default_severity,
            "active": item.active,
        }
        for item in task.checklist_items
    ]


def orm_to_result(row) -> ResultRecord:
    return ResultRecord(
        id=row.id,
        task_id=row.task_id,
        device_id=row.device_id,
        item_code=row.item_code,
        result_status=row.result_status,
        measured_value=row.measured_value or "",
        photo_url=row.photo_url or "",
        note=row.note or "",
        review_state=row.review_state,
        severity_hint=row.severity_hint,
        revision=row.revision,
        submitted_at=row.submitted_at,
        reviewed_at=row.reviewed_at,
        returned_at=row.returned_at,
    )


def apply_result_to_orm(result: ResultRecord, row) -> None:
    row.result_status = result.result_status
    row.measured_value = result.measured_value
    row.photo_url = result.photo_url
    row.note = result.note
    row.review_state = result.review_state
    row.severity_hint = result.severity_hint
    row.revision = result.revision
    row.submitted_at = result.submitted_at
    row.reviewed_at = result.reviewed_at
    row.returned_at = result.returned_at


def orm_to_hazard(row) -> HazardRecord:
    return HazardRecord(
        id=row.id,
        result_id=row.result_id,
        device_id=row.device_id,
        task_id=row.task_id,
        severity=row.severity,
        owner_id=row.owner_id,
        deadline=row.deadline or "",
        rectify_status=row.rectify_status,
        rectify_note=row.rectify_note or "",
        closed_at=row.closed_at,
        created_at=row.created_at or "",
    )


def apply_hazard_to_orm(hazard: HazardRecord, row) -> None:
    row.severity = hazard.severity
    row.owner_id = hazard.owner_id
    row.deadline = hazard.deadline
    row.rectify_status = hazard.rectify_status
    row.rectify_note = hazard.rectify_note
    row.closed_at = hazard.closed_at
    row.created_at = hazard.created_at
    row.active_key = "ACTIVE" if hazard.rectify_status in ("OPEN", "RECTIFIED") else None


def orm_to_device(row) -> DeviceRecord:
    return DeviceRecord(
        id=row.id,
        building_id=row.building_id,
        device_code=row.device_code,
        device_type=row.device_type,
        floor=row.floor,
        location_desc=row.location_desc,
        install_date=row.install_date,
        status=row.status,
        next_maintenance_at=row.next_maintenance_at,
        owner_id=row.owner_id,
    )
