from pydantic import BaseModel
class ConflictEntry(BaseModel):
    id: int | float
    task_id: int | float
    submission_id: str
    revision: int
    current_revision: int
    payload: dict
    reason: str
    created_at: str
