def create_inspection_task_dto(**overrides):
    row = {"id":1,"building_id":1,"inspector_id":1,"plan_date":"2026-06-11T09:00:00Z","task_type":"HYDRANT","status":"IN_PROGRESS","checklist_version":"checklist version 1","finished_at":"2026-06-11T09:00:00Z"}
    row.update(overrides)
    return row
