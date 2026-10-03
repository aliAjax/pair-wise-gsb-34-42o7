"""复核链仓储：把 ORM 行转领域对象，引擎变更后再统一落库。

ORM 相关导入全部惰性化，使 service/领域层在没有 SQLAlchemy 的环境也可单测。
"""

from src.constructors.persistence_mapper import (
    apply_hazard_to_orm,
    apply_result_to_orm,
    apply_task_to_orm,
    orm_to_device,
    orm_to_hazard,
    orm_to_result,
    orm_to_task,
)
from src.domain.records import AuditEventRecord, ConflictRecord, HazardRecord, ResultRecord, TaskRecord, utc_now_iso


def _model(name: str):
    from src.models import (
        audit_log as _audit,
        building as _building,
        fire_device as _device,
        hazard_ticket as _hazard,
        inspection_result as _result,
        inspection_task as _task,
        submission_conflict as _conflict,
        submission_record as _submission,
        user_account as _user,
    )

    return {
        "AuditLog": _audit.AuditLog,
        "Building": _building.Building,
        "FireDevice": _device.FireDevice,
        "HazardTicket": _hazard.HazardTicket,
        "InspectionResult": _result.InspectionResult,
        "InspectionTask": _task.InspectionTask,
        "SubmissionConflict": _conflict.SubmissionConflict,
        "SubmissionRecord": _submission.SubmissionRecord,
        "UserAccount": _user.UserAccount,
    }[name]


def _select(model):
    from sqlalchemy import select

    return select(model)


class ChainRepository:
    """复核链读写仓储：把 ORM 行转领域对象，引擎变更后再统一落库。"""

    def __init__(self, db):
        self.db = db

    # ------------------------------------------------------------ queries

    def get_task_orm(self, task_id: int):
        return self.db.get(_model("InspectionTask"), task_id)

    def get_task(self, task_id: int) -> TaskRecord:
        row = self.get_task_orm(task_id)
        return orm_to_task(row) if row else None

    def list_results(self, task_id: int) -> list[ResultRecord]:
        rows = self.db.scalars(
            _select(_model("InspectionResult")).where(_model("InspectionResult").task_id == task_id)
        ).all()
        return [orm_to_result(r) for r in rows]

    def list_all_results(self) -> list:
        return self.db.scalars(_select(_model("InspectionResult"))).all()

    def list_hazards(self) -> list[HazardRecord]:
        rows = self.db.scalars(_select(_model("HazardTicket"))).all()
        return [orm_to_hazard(r) for r in rows]

    def list_all_hazards_orm(self):
        return self.db.scalars(_select(_model("HazardTicket"))).all()

    def get_hazard_orm(self, hazard_id: int):
        return self.db.get(_model("HazardTicket"), hazard_id)

    def list_devices(self):
        return [orm_to_device(r) for r in self.db.scalars(_select(_model("FireDevice"))).all()]

    def list_device_rows(self):
        return self.db.scalars(_select(_model("FireDevice"))).all()

    def get_result_orm_by_id(self, result_id: int):
        return self.db.get(_model("InspectionResult"), result_id)

    def get_result_orm(self, task_id: int, item_code: str):
        result_model = _model("InspectionResult")
        return self.db.scalars(
            _select(result_model).where(
                result_model.task_id == task_id,
                result_model.item_code == item_code,
                result_model.review_state != "DISCARDED",
            )
        ).first()

    # ------------------------------------------------------------ mutations

    def find_result_row(self, task_id: int, result_id: int):
        result_model = _model("InspectionResult")
        return self.db.scalars(
            _select(result_model).where(
                result_model.task_id == task_id,
                result_model.id == result_id,
            )
        ).first()

    def persist_task(self, task: TaskRecord) -> None:
        row = self.get_task_orm(task.id)
        if row is not None:
            apply_task_to_orm(task, row)

    def upsert_result(self, result: ResultRecord):
        row = self.find_result_row(result.task_id, result.id) if result.id else None
        if row is None:
            row = _model("InspectionResult")(
                task_id=result.task_id,
                device_id=result.device_id,
                item_code=result.item_code,
            )
            self.db.add(row)
            self.db.flush()
            result.id = row.id
        apply_result_to_orm(result, row)
        return row

    def upsert_hazard(self, hazard: HazardRecord):
        row = self.db.get(_model("HazardTicket"), hazard.id) if hazard.id else None
        if row is None:
            row = _model("HazardTicket")(
                result_id=hazard.result_id,
                device_id=hazard.device_id,
                task_id=hazard.task_id,
                created_at=hazard.created_at or utc_now_iso(),
            )
            self.db.add(row)
            self.db.flush()
            hazard.id = row.id
        apply_hazard_to_orm(hazard, row)
        return row

    def add_conflict(self, conflict: ConflictRecord):
        row = _model("SubmissionConflict")(
            task_id=conflict.task_id,
            client_submission_id=conflict.client_submission_id,
            base_revision=conflict.base_revision,
            current_revision=conflict.current_revision,
            reason=conflict.reason,
            payload_preview=conflict.payload_preview,
            created_at=conflict.created_at or utc_now_iso(),
        )
        self.db.add(row)
        self.db.flush()
        conflict.id = row.id
        return row

    def list_conflicts(self, task_id: int | None = None):
        model = _model("SubmissionConflict")
        stmt = _select(model).order_by(model.id.desc())
        if task_id is not None:
            stmt = stmt.where(model.task_id == task_id)
        return self.db.scalars(stmt).all()

    def add_audit_events(self, events: list[AuditEventRecord]) -> None:
        audit_model = _model("AuditLog")
        for event in events:
            self.db.add(
                audit_model(
                    actor_id=event.actor_id,
                    actor_role=event.actor_role,
                    action=event.action,
                    target_type=event.target_type,
                    target_id=event.target_id,
                    detail=event.detail,
                    created_at=event.created_at or utc_now_iso(),
                )
            )

    def list_audit_logs(self, target_id: str | None = None, target_type: str | None = None):
        model = _model("AuditLog")
        stmt = _select(model).order_by(model.id.desc())
        if target_id is not None:
            stmt = stmt.where(model.target_id == str(target_id))
        if target_type is not None:
            stmt = stmt.where(model.target_type == target_type)
        return self.db.scalars(stmt).all()

    # ----------------------------------------------------- idempotency record

    def get_submission_record(self, task_id: int, client_submission_id: str):
        model = _model("SubmissionRecord")
        return self.db.scalars(
            _select(model).where(
                model.task_id == task_id,
                model.client_submission_id == client_submission_id,
            )
        ).first()

    def save_submission_record(self, task_id: int, client_submission_id: str,
                               inspector_id: int, base_revision: int, outcome_json: dict):
        row = self.get_submission_record(task_id, client_submission_id)
        if row is None:
            row = _model("SubmissionRecord")(
                task_id=task_id,
                client_submission_id=client_submission_id,
                inspector_id=inspector_id,
                base_revision=base_revision,
                created_at=utc_now_iso(),
            )
            self.db.add(row)
        row.outcome_json = outcome_json
        return row

    # --------------------------------------------------------------- users

    def get_user_by_name(self, username: str):
        model = _model("UserAccount")
        return self.db.scalars(_select(model).where(model.username == username)).first()

    def get_user(self, user_id: int):
        return self.db.get(_model("UserAccount"), user_id)
