"""复核链接口的 Pydantic 请求模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginPayload(BaseModel):
    username: str
    password: str


class ChecklistItemInput(BaseModel):
    item_code: str = Field(min_length=1, max_length=64)
    device_id: int
    title: str = ""
    default_severity: str = "MEDIUM"


class ChecklistItemPatch(BaseModel):
    item_code: str
    title: str | None = None
    default_severity: str | None = None


class TaskCreatePayload(BaseModel):
    building_id: int
    inspector_id: int
    plan_date: str
    task_type: str = "ROUTINE"
    checklist_items: list[ChecklistItemInput] = Field(default_factory=list)


class SubmitItemPayload(BaseModel):
    item_code: str
    result_status: str  # PENDING / NORMAL / ABNORMAL
    measured_value: str = ""
    photo_url: str = ""
    note: str = ""
    severity_hint: str | None = None
    owner_id: int | None = None
    deadline: str | None = None


class SubmitTaskPayload(BaseModel):
    # 客户端生成的幂等键：同一提交重试只生成一张隐患单
    client_submission_id: str = Field(min_length=1, max_length=128)
    # 本次提交所基于的任务修订号；过期修订整包进冲突区
    base_revision: int
    # 断网恢复后从完整任务继续提交：允许携带全量检查项
    items: list[SubmitItemPayload]


class ReviewPayload(BaseModel):
    decision: str  # APPROVE / RETURN
    item_codes: list[str]
    note: str = ""


class ChecklistChangePayload(BaseModel):
    added: list[ChecklistItemInput] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    updated: list[ChecklistItemPatch] = Field(default_factory=list)


class AssignHazardPayload(BaseModel):
    owner_id: int


class RectifyHazardPayload(BaseModel):
    rectify_note: str = ""


class VerifyHazardPayload(BaseModel):
    approved: bool
    note: str = ""
