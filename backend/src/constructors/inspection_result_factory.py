def create_inspection_result_dto(**overrides):
    row = {
        "id": 0,
        "task_id": 0,
        "device_id": 0,
        "item_code": "",
        "result_status": "PENDING",
        "measured_value": "",
        "photo_url": "",
        "note": "",
        "review_state": "DRAFT",
        "severity_hint": "MEDIUM",
        "revision": 1,
        "submitted_at": None,
        "reviewed_at": None,
        "returned_at": None,
    }
    row.update(overrides)
    return row
