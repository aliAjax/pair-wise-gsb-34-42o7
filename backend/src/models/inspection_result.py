from pydantic import BaseModel
class InspectionResult(BaseModel):
    id: int | float
    task_id: int | float
    device_id: int | float
    item_code: str
    result_status: str
    measured_value: str
    photo_url: str
    note: str
