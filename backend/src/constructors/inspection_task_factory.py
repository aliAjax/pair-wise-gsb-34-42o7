def create_inspection_task_dto(**overrides):
    row = {
        "id": 0,
        "building_id": 1,
        "inspector_id": 1,
        "plan_date": "2026-10-03",
        "task_type": "ROUTINE",
        "status": "PLANNED",
        "checklist_version": "v1",
        "finished_at": None,
        "revision": 1,
        "checklist_items": [],
    }
    row.update(overrides)
    return row
