from pydantic import BaseModel
class HazardTicket(BaseModel):
    id: int | float
    result_id: int | float
    device_id: int | float
    item_code: str
    severity: str
    owner_id: int | float
    deadline: str
    rectify_status: str
    rectify_note: str
    submission_id: str
    closed_at: str
