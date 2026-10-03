from pydantic import BaseModel
class InspectionTask(BaseModel):
    id: int | float
    building_id: int | float
    inspector_id: int | float
    plan_date: str
    task_type: str
    status: str
    checklist_version: str
    finished_at: str
