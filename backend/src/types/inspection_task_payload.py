from pydantic import BaseModel

InspectionTaskPayload = dict

class SubmitResultItem(BaseModel):
    device_id: int
    item_code: str
    result_status: str
    measured_value: str = ""
    photo_url: str = ""
    note: str = ""
    severity: str = "MEDIUM"

class SubmitTaskPayload(BaseModel):
    """提交复核：必须带任务修订号和幂等提交号，断网恢复后整包重投。"""
    revision: int
    submission_id: str
    results: list[SubmitResultItem] = []

class RejectTaskPayload(BaseModel):
    """复核退回：只放开被点名的检查项。"""
    item_codes: list[str]
    note: str = ""
