from pydantic import BaseModel
class FireDevice(BaseModel):
    id: int | float
    building_id: int | float
    device_code: str
    device_type: str
    floor: str
    location_desc: str
    install_date: str
    status: str
    next_maintenance_at: str
