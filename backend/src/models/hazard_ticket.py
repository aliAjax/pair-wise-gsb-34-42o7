from pydantic import BaseModel
class HazardTicket(BaseModel):
    id: int | float
    result_id: int | float
    severity: str
    owner_id: int | float
    deadline: str
    rectify_status: str
    rectify_note: str
    closed_at: str
