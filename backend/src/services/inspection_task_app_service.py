"""巡检任务服务：建档/排期、列表、完整任务拉取。"""

from sqlalchemy.orm import Session

from src.constants.inspection_status import InspectionStatus
from src.constructors.chain_dto_builder import build_full_task_dto, build_result_dto, build_task_dto
from src.domain import errors
from src.models.inspection_result import InspectionResult
from src.models.inspection_task import InspectionTask
from src.services.chain_service import ChainService


class InspectionTaskAppService:
    def __init__(self, db: Session):
        self.db = db

    def list_tasks(self, building_id: int | None = None, inspector_id: int | None = None):
        query = self.db.query(InspectionTask)
        if building_id is not None:
            query = query.filter(InspectionTask.building_id == building_id)
        if inspector_id is not None:
            query = query.filter(InspectionTask.inspector_id == inspector_id)
        return [build_task_dto(row) for row in query.order_by(InspectionTask.id.desc()).all()]

    def create_task(self, payload, actor_id: int) -> dict:
        if not payload.checklist_items:
            raise errors.ValidationChainError("checklist_items 不能为空")
        row = InspectionTask(
            building_id=payload.building_id,
            inspector_id=payload.inspector_id,
            plan_date=payload.plan_date,
            task_type=payload.task_type,
            status=InspectionStatus.PLANNED,
            checklist_version="v1",
            revision=1,
            checklist_items=[
                {
                    "item_code": item.item_code,
                    "device_id": item.device_id,
                    "title": item.title,
                    "default_severity": item.default_severity,
                    "active": True,
                }
                for item in payload.checklist_items
            ],
        )
        self.db.add(row)
        self.db.flush()
        # 为每个检查项预建 PENDING/DRAFT 结果，保证从完整任务离线续传
        for item in payload.checklist_items:
            self.db.add(
                InspectionResult(
                    task_id=row.id,
                    device_id=item.device_id,
                    item_code=item.item_code,
                    result_status="PENDING",
                    review_state="DRAFT",
                    severity_hint=item.default_severity,
                    revision=1,
                )
            )
        self.db.commit()
        return build_task_dto(row)

    def full_task(self, task_id: int) -> dict:
        chain = ChainService(self.db)
        task_row, result_rows = chain.full_task(task_id)
        return build_full_task_dto(task_row, result_rows)

    def task_results(self, task_id: int):
        rows = (
            self.db.query(InspectionResult)
            .filter(InspectionResult.task_id == task_id)
            .order_by(InspectionResult.id.asc())
            .all()
        )
        return [build_result_dto(r) for r in rows]
