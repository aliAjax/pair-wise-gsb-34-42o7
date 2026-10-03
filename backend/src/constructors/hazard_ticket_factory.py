def create_hazard_ticket_dto(**overrides):
    row = {
        "id": 0,
        "result_id": 0,
        "device_id": 0,
        "task_id": 0,
        "severity": "MEDIUM",
        "owner_id": 0,
        "deadline": "",
        "rectify_status": "OPEN",
        "rectify_note": "",
        "closed_at": None,
        "created_at": None,
    }
    row.update(overrides)
    return row
