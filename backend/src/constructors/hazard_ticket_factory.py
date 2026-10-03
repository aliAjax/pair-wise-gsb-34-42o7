def create_hazard_ticket_dto(**overrides):
    row = {"id":1,"result_id":1,"severity":"severity 1","owner_id":1,"deadline":"deadline 1","rectify_status":"IN_PROGRESS","rectify_note":"rectify note 1","closed_at":"2026-06-11T09:00:00Z"}
    row.update(overrides)
    return row
