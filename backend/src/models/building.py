from pydantic import BaseModel
class Building(BaseModel):
    id: int | float
    name: str
    campus: str
    floor_count: int | float
    fire_grade: str
    manager_id: int | float
    address_code: str
