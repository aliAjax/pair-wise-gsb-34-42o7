"""复核链应用服务：事务编排、幂等回放、冲突落库、设备合规重算。"""

from __future__ import annotations

from src.constructors.persistence_mapper import orm_to_hazard
from src.domain import errors
from src.domain.review_chain_engine import (
    ChecklistChanges,
    IdProvider,
    ReviewChainEngine,
    SubmittedItem,
)
from src.repositories.chain_repository import ChainRepository


class _DbIdProvider(IdProvider):
    """优先用数据库序列，保证 ORM 自增 id 与领域 id 一致。"""

    def __init__(self, db):
        self.db = db

    def new(self, table: str) -> int:
        return 0  # 实际 id 在 flush 后由 ORM 回填，占位即可


def _hazard_outcome_payload(outcome) -> dict:
    return {
        "state": outcome.state,
        "task_id": outcome.task_id,
        "base_revision": outcome.base_revision,
        "new_revision": outcome.new_revision,
        "accepted_items": outcome.accepted_items,
        "conflicts": outcome.conflicts,
        "hazard_ids_created": [h.id for h in outcome.hazards_created],
        "hazard_ids_cancelled": [h.id for h in outcome.hazards_cancelled],
        "replayed": True,
    }


class ChainService:
    def __init__(self, db):
        self.db = db
        self.repo = ChainRepository(db)

    # ------------------------------------------------------------- submit

    def submit_full_task(self, task_id: int, payload: dict, actor_id: int, actor_role: str) -> dict:
        client_submission_id = str(payload.get("client_submission_id") or "").strip()
        if not client_submission_id:
            raise errors.ValidationChainError("client_submission_id is required")
        base_revision = int(payload.get("base_revision") or 0)
        items_payload = payload.get("items") or []
        if not items_payload:
            raise errors.ValidationChainError("items is required for full-task submit")

        # 幂等：同一提交重试直接回放首次结果，不重复生成隐患单
        replay = self.repo.get_submission_record(task_id, client_submission_id)
        if replay is not None:
            return replay.outcome_json

        task_row = self.repo.get_task_orm(task_id)
        if task_row is None:
            raise errors.NotFoundError(f"task {task_id} not found")
        task = self.repo.get_task(task_id)
        results = self.repo.list_results(task_id)
        hazards = self.repo.list_hazards()

        engine = ReviewChainEngine(_DbIdProvider(self.db))
        items = [
            SubmittedItem(
                item_code=i["item_code"],
                result_status=i["result_status"],
                measured_value=i.get("measured_value", ""),
                photo_url=i.get("photo_url", ""),
                note=i.get("note", ""),
                severity_hint=i.get("severity_hint"),
                owner_id=i.get("owner_id"),
                deadline=i.get("deadline"),
            )
            for i in items_payload
        ]

        try:
            outcome = engine.submit_results(
                task, results, hazards, base_revision, items,
                actor_id, actor_role, client_submission_id,
            )
        except errors.StaleRevisionError:
            # 过期修订整包进冲突区；本次请求不写任何结果
            self._persist_engine_conflicts(engine)
            self.db.commit()
            raise
        except Exception:
            self.db.rollback()
            raise

        try:
            # 落库：任务、结果、隐患（新建先 flush 拿 id）
            self.repo.persist_task(task)
            for result in results:
                self.repo.upsert_result(result)
            self.db.flush()
            abnormal_accepted = {
                r.item_code: r.id
                for r in results
                if r.task_id == task_id
                and r.item_code in outcome.accepted_items
                and r.result_status == "ABNORMAL"
            }
            for hazard in outcome.hazards_created:
                if not hazard.result_id and hazard.item_code in abnormal_accepted:
                    hazard.result_id = abnormal_accepted[hazard.item_code]
                self.repo.upsert_hazard(hazard)
            for hazard in outcome.hazards_cancelled:
                self.repo.upsert_hazard(hazard)
            self.repo.add_audit_events(engine.events)
            self.db.flush()

            payload_out = _hazard_outcome_payload(outcome)
            self.repo.save_submission_record(
                task_id, client_submission_id, actor_id, base_revision, payload_out,
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return payload_out

    def _persist_engine_conflicts(self, engine: ReviewChainEngine) -> None:
        for conflict in engine.conflicts:
            self.repo.add_conflict(conflict)
        self.repo.add_audit_events(engine.events)

    # ------------------------------------------------------------- review

    def review(self, task_id: int, payload: dict, actor_id: int, actor_role: str) -> dict:
        task_row = self.repo.get_task_orm(task_id)
        if task_row is None:
            raise errors.NotFoundError(f"task {task_id} not found")
        task = self.repo.get_task(task_id)
        results = self.repo.list_results(task_id)

        engine = ReviewChainEngine(_DbIdProvider(self.db))
        outcome = engine.review_results(
            task, results,
            decision=payload["decision"],
            item_codes=list(payload.get("item_codes", [])),
            note=payload.get("note", ""),
            actor_id=actor_id,
            actor_role=actor_role,
        )
        self.repo.persist_task(task)
        for result in outcome["results_touched"]:
            self.repo.upsert_result(result)
        self.repo.add_audit_events(engine.events)
        self.db.commit()
        return {
            "decision": outcome["decision"],
            "item_codes": outcome["item_codes"],
            "new_revision": outcome["new_revision"],
            "task_status": outcome["task_status"],
            "replayed": False,
        }

    # ------------------------------------------------------ checklist edit

    def change_checklist(self, task_id: int, payload: dict, actor_id: int, actor_role: str) -> dict:
        task_row = self.repo.get_task_orm(task_id)
        if task_row is None:
            raise errors.NotFoundError(f"task {task_id} not found")
        task = self.repo.get_task(task_id)
        results = self.repo.list_results(task_id)
        hazards = self.repo.list_hazards()
        changes = ChecklistChanges(
            added=[_to_checklist_item(i) for i in payload.get("added", [])],
            removed=list(payload.get("removed", [])),
            updated=list(payload.get("updated", [])),
        )

        engine = ReviewChainEngine(_DbIdProvider(self.db))
        outcome = engine.change_checklist(
            task, results, hazards, changes, actor_id, actor_role,
        )
        self.repo.persist_task(task)
        for result in results:
            self.repo.upsert_result(result)
        self.db.flush()
        # 在途隐患单：撤销的落库；等级被检查项修改重判的回写
        cancelled_ids = {id(h) for h in outcome["cancelled_hazards"]}
        reseverity_codes = {u.get("item_code") for u in changes.updated if u.get("default_severity")}
        for hazard in hazards:
            related_result = next((r for r in results if r.id == hazard.result_id), None)
            if id(hazard) in cancelled_ids:
                self.repo.upsert_hazard(hazard)
            elif (
                related_result is not None
                and related_result.item_code in reseverity_codes
                and hazard.rectify_status in ("OPEN", "RECTIFIED")
            ):
                self.repo.upsert_hazard(hazard)
        self.repo.add_audit_events(engine.events)
        self.db.commit()
        return {
            "added": [i.item_code for i in outcome["added"]],
            "removed": changes.removed,
            "updated": [u.get("item_code") for u in changes.updated],
            "discarded": [r.item_code for r in outcome["discarded"]],
            "cancelled_hazard_ids": [h.id for h in outcome["cancelled_hazards"]],
            "new_revision": outcome["new_revision"],
            "task_status": outcome["task_status"],
        }

    # ------------------------------------------------------------- hazard

    def _load_hazard(self, hazard_id: int):
        row = self.repo.get_hazard_orm(hazard_id)
        if row is None:
            raise errors.NotFoundError(f"hazard {hazard_id} not found")
        return row, orm_to_hazard(row)

    def assign_hazard(self, hazard_id: int, owner_id: int, actor_id: int, actor_role: str):
        row, hazard = self._load_hazard(hazard_id)
        engine = ReviewChainEngine(_DbIdProvider(self.db))
        engine.assign_hazard(hazard, owner_id, actor_id, actor_role)
        self.repo.upsert_hazard(hazard)
        self.repo.add_audit_events(engine.events)
        self.db.commit()
        return row

    def rectify_hazard(self, hazard_id: int, note: str, actor_id: int, actor_role: str):
        row, hazard = self._load_hazard(hazard_id)
        engine = ReviewChainEngine(_DbIdProvider(self.db))
        engine.rectify_hazard(hazard, note, actor_id, actor_role)
        self.repo.upsert_hazard(hazard)
        self.repo.add_audit_events(engine.events)
        self.db.commit()
        return row

    def verify_hazard(self, hazard_id: int, approved: bool, note: str,
                      actor_id: int, actor_role: str):
        row, hazard = self._load_hazard(hazard_id)
        engine = ReviewChainEngine(_DbIdProvider(self.db))
        engine.verify_hazard(hazard, approved, note, actor_id, actor_role)
        self.repo.upsert_hazard(hazard)
        self.repo.add_audit_events(engine.events)
        self.db.commit()
        return row

    # ------------------------------------------------------------ queries

    def full_task(self, task_id: int) -> tuple:
        task_row = self.repo.get_task_orm(task_id)
        if task_row is None:
            raise errors.NotFoundError(f"task {task_id} not found")
        result_rows = self.repo.list_all_results()
        result_rows = [r for r in result_rows if r.task_id == task_id]
        return task_row, result_rows

    def conflicts(self, task_id: int | None = None):
        return self.repo.list_conflicts(task_id)

    def audit_logs(self, target_id=None, target_type=None):
        return self.repo.list_audit_logs(target_id, target_type)


def _to_checklist_item(payload: dict):
    from src.domain.records import ChecklistItemRecord

    return ChecklistItemRecord(
        item_code=payload["item_code"],
        device_id=int(payload["device_id"]),
        title=payload.get("title", ""),
        default_severity=payload.get("default_severity", "MEDIUM"),
    )
