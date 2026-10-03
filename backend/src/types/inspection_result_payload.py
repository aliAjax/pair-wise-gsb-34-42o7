from pydantic import BaseModel

InspectionResultPayload = dict

class UpdateResultPayload(BaseModel):
    """检查项修改：仅允许被退回点名或待提交的检查项，保存后重算隐患与设备状态。"""
    result_status: str | None = None
    measured_value: str | None = None
    photo_url: str | None = None
    note: str | None = None
    severity: str = "MEDIUM"
