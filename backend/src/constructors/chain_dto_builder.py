"""复核链响应 DTO 构造器：页面/store 不直接散写响应结构。"""

from __future__ import annotations

from src.constructors.persistence_mapper import (
    orm_to_device,
    orm_to_hazard,
    orm_to_result,
    orm_to_task,
)
from src.domain.compliance import recompute_device_compliance


def build_task_dto(row) -> dict:
    task = orm_to_task(row)
    return {
        "id": task.id,
        "building_id": task.building_id,
        "inspector_id": task.inspector_id,
        "plan_date": task.plan_date,
        "task_type": task.task_type,
        "status": task.status,
        "checklist_version": task.checklist_version,
        "finished_at": task.finished_at,
        "revision": task.revision,
        "checklist_items": [
            {
                "item_code": i.item_code,
                "device_id": i.device_id,
                "title": i.title,
                "default_severity": i.default_severity,
                "active": i.active,
            }
            for i in task.checklist_items
        ],
    }


def build_full_task_dto(task_row, result_rows) -> dict:
    """断网恢复后拉取的完整任务：任务+修订号+全部检查项结果。"""

    dto = build_task_dto(task_row)
    dto["results"] = [build_result_dto(r) for r in result_rows]
    return dto


def build_result_dto(row) -> dict:
    result = orm_to_result(row)
    return {
        "id": result.id,
        "task_id": result.task_id,
        "device_id": result.device_id,
        "item_code": result.item_code,
        "result_status": result.result_status,
        "measured_value": result.measured_value,
        "photo_url": result.photo_url,
        "note": result.note,
        "review_state": result.review_state,
        "severity_hint": result.severity_hint,
        "revision": result.revision,
        "submitted_at": result.submitted_at,
        "reviewed_at": result.reviewed_at,
        "returned_at": result.returned_at,
    }


def build_hazard_dto(row, device_rows=None) -> dict:
    hazard = orm_to_hazard(row)
    dto = {
        "id": hazard.id,
        "result_id": hazard.result_id,
        "device_id": hazard.device_id,
        "task_id": hazard.task_id,
        "severity": hazard.severity,
        "owner_id": hazard.owner_id,
        "deadline": hazard.deadline,
        "rectify_status": hazard.rectify_status,
        "rectify_note": hazard.rectify_note,
        "closed_at": hazard.closed_at,
        "created_at": hazard.created_at,
    }
    if device_rows is not None:
        device = next((d for d in device_rows if d.id == hazard.device_id), None)
        if device is not None:
            dto["device_code"] = device.device_code
    return dto


def build_device_dto(row, hazards) -> dict:
    """台账 DTO：status 返回由隐患重算的合规状态；主数据状态保留在 base_status。"""

    device = orm_to_device(row)
    compliance = recompute_device_compliance(device, hazards)
    return {
        "id": device.id,
        "building_id": device.building_id,
        "device_code": device.device_code,
        "device_type": device.device_type,
        "floor": device.floor,
        "location_desc": device.location_desc,
        "install_date": device.install_date,
        "status": compliance,
        "base_status": device.status,
        "next_maintenance_at": device.next_maintenance_at,
        "owner_id": device.owner_id,
    }


def build_audit_dto(row) -> dict:
    return {
        "id": row.id,
        "actor_id": row.actor_id,
        "actor_role": row.actor_role,
        "action": row.action,
        "target_type": row.target_type,
        "target_id": row.target_id,
        "detail": row.detail,
        "created_at": row.created_at,
    }


def build_conflict_dto(row) -> dict:
    return {
        "id": row.id,
        "task_id": row.task_id,
        "client_submission_id": row.client_submission_id,
        "base_revision": row.base_revision,
        "current_revision": row.current_revision,
        "reason": row.reason,
        "payload_preview": row.payload_preview,
        "created_at": row.created_at,
    }
