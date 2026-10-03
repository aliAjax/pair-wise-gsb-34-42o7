"""复核链核心引擎（纯标准库，不依赖 FastAPI/SQLAlchemy）。

覆盖：
- 提交携带任务修订号：过期修订整包进冲突区，绝不覆盖现结果；
- 已复核检查项受保护：当前修订下也逐项拒绝，其余检查项照常受理（部分受理）；
- 同一提交重试：service 层按 client_submission_id 幂等回放，引擎层保证一个结果至多一张在途隐患单；
- 检查项修改：废弃结果、撤销/重判隐患、自增修订号；
- 复核退回：只放开被点名检查项，其余结果原状不动；
- 设备合规状态由未关闭隐患实时重算，高危隐患一票否决；
- 所有写动作产生审计事件。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.constants.device_compliance import DeviceBaseStatus
from src.constants.hazard_severity import HazardRectifyStatus, HazardSeverity
from src.constants.inspection_status import InspectionStatus
from src.constants.log_templates import AuditAction
from src.constants.result_status import ResultStatus
from src.constants.review_state import ReviewDecision, ReviewState
from src.constants.submission_conflict import ConflictReason, SubmissionState
from src.constants.user_role import UserRole
from src.domain import errors
from src.domain.records import (
    AuditEventRecord,
    ChecklistItemRecord,
    ConflictRecord,
    HazardRecord,
    ResultRecord,
    TaskRecord,
    utc_now_iso,
)


@dataclass
class SubmittedItem:
    item_code: str
    result_status: str
    measured_value: str = ""
    photo_url: str = ""
    note: str = ""
    severity_hint: str | None = None
    owner_id: int | None = None
    deadline: str | None = None


@dataclass
class ChecklistChanges:
    added: list[ChecklistItemRecord] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    updated: list[dict] = field(default_factory=list)


@dataclass
class SubmissionOutcome:
    state: str
    task_id: int
    base_revision: int
    new_revision: int
    accepted_items: list[str] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    hazards_created: list[HazardRecord] = field(default_factory=list)
    hazards_cancelled: list[HazardRecord] = field(default_factory=list)
    results_touched: list[ResultRecord] = field(default_factory=list)


class IdProvider:
    """测试用自增 id 提供器；生产 service 用数据库序列实现同名接口。"""

    def __init__(self, start: int = 1):
        self._next = start

    def new(self, _table: str) -> int:
        value = self._next
        self._next += 1
        return value


class ReviewChainEngine:
    def __init__(self, id_provider: IdProvider | None = None):
        self.id_provider = id_provider or IdProvider()
        self.events: list[AuditEventRecord] = []
        self.conflicts: list[ConflictRecord] = []

    # ------------------------------------------------------------------ utils

    def _new_id(self, table: str) -> int:
        return self.id_provider.new(table)

    def _audit(self, actor_id: int, actor_role: str, action: str, target_type: str,
               target_id, detail: str = "") -> None:
        self.events.append(
            AuditEventRecord(
                id=None,
                actor_id=actor_id,
                actor_role=actor_role,
                action=action,
                target_type=target_type,
                target_id=str(target_id),
                detail=detail,
            )
        )

    @staticmethod
    def _require_role(actor_role: str, allowed: tuple[str, ...]) -> None:
        if actor_role not in allowed:
            raise errors.RbacDeniedError(f"role {actor_role} not in {allowed}")

    @staticmethod
    def _active_item(task: TaskRecord, item_code: str) -> ChecklistItemRecord | None:
        return next(
            (i for i in task.checklist_items if i.item_code == item_code and i.active),
            None,
        )

    def _active_result(self, results, task_id: int, item_code: str) -> ResultRecord | None:
        return next(
            (
                r
                for r in results
                if r.task_id == task_id
                and r.item_code == item_code
                and r.review_state != ReviewState.DISCARDED
            ),
            None,
        )

    def _open_hazard(self, hazards, result_id: int) -> HazardRecord | None:
        return next(
            (
                h
                for h in hazards
                if h.result_id == result_id
                and h.rectify_status in HazardRectifyStatus.OPEN_LIKE
            ),
            None,
        )

    @classmethod
    def aggregate_task_status(cls, task: TaskRecord, results) -> str:
        active_codes = [i.item_code for i in task.checklist_items if i.active]
        if not active_codes:
            return task.status if task.status in InspectionStatus.ALL else InspectionStatus.PLANNED
        active_results = [
            r
            for r in results
            if r.task_id == task.id and r.item_code in active_codes and r.review_state != ReviewState.DISCARDED
        ]
        by_code = {r.item_code: r for r in active_results}
        states = [by_code[c].review_state if c in by_code else ReviewState.DRAFT for c in active_codes]
        if states and all(s == ReviewState.REVIEWED for s in states):
            return InspectionStatus.REVIEWED
        if ReviewState.RETURNED in states:
            return InspectionStatus.RETURNED
        if any(s == ReviewState.SUBMITTED for s in states):
            return InspectionStatus.SUBMITTED
        if any(s == ReviewState.DRAFT for s in states):
            return InspectionStatus.IN_PROGRESS
        return InspectionStatus.IN_PROGRESS

    # ------------------------------------------------------------ submission

    def submit_results(
        self,
        task: TaskRecord,
        results: list[ResultRecord],
        hazards: list[HazardRecord],
        base_revision: int,
        items: list[SubmittedItem],
        actor_id: int,
        actor_role: str,
        client_submission_id: str,
    ) -> SubmissionOutcome:
        self._require_role(actor_role, (UserRole.INSPECTOR,))
        if task.inspector_id != actor_id:
            raise errors.RbacDeniedError("task assigned to another inspector")
        if not items:
            raise errors.ValidationChainError("empty submission items")

        # 守卫 1：过期修订号整包进冲突区，任何现结果都不允许被覆盖。
        if base_revision != task.revision:
            conflict = ConflictRecord(
                id=self._new_id("submission_conflict"),
                task_id=task.id,
                client_submission_id=client_submission_id,
                base_revision=base_revision,
                current_revision=task.revision,
                reason=ConflictReason.STALE_TASK_REVISION,
                payload_preview=",".join(i.item_code for i in items),
            )
            self.conflicts.append(conflict)
            self._audit(
                actor_id, actor_role, AuditAction.SUBMISSION_CONFLICT,
                "InspectionTask", task.id,
                f"base_revision={base_revision} current={task.revision} items={len(items)}",
            )
            raise errors.StaleRevisionError(
                details={"conflict_id": conflict.id, "current_revision": task.revision},
            )

        outcome = SubmissionOutcome(
            state=SubmissionState.ACCEPTED,
            task_id=task.id,
            base_revision=base_revision,
            new_revision=task.revision,
        )
        new_revision = task.revision

        for item in items:
            checklist_item = self._active_item(task, item.item_code)
            if checklist_item is None:
                raise errors.ValidationChainError(
                    f"item {item.item_code} not in active checklist",
                    details={"item_code": item.item_code},
                )
            result = self._active_result(results, task.id, item.item_code)

            # 守卫 2：已复核结果逐项保护；其余项继续受理。
            if result is not None and result.review_state == ReviewState.REVIEWED:
                outcome.conflicts.append(
                    {"item_code": item.item_code, "reason": ConflictReason.REVIEWED_PROTECTED}
                )
                continue

            # PENDING 只代表“未检”，保持草稿，不触发复核链。
            if item.result_status == ResultStatus.PENDING:
                if result is None:
                    result = ResultRecord(
                        id=self._new_id("inspection_result"),
                        task_id=task.id,
                        device_id=checklist_item.device_id,
                        item_code=item.item_code,
                        result_status=ResultStatus.PENDING,
                        review_state=ReviewState.DRAFT,
                        severity_hint=checklist_item.default_severity,
                    )
                    results.append(result)
                self._touch_draft(result, item)
                outcome.results_touched.append(result)
                continue

            if result is None:
                result = ResultRecord(
                    id=self._new_id("inspection_result"),
                    task_id=task.id,
                    device_id=checklist_item.device_id,
                    item_code=item.item_code,
                    result_status=item.result_status,
                    review_state=ReviewState.SUBMITTED,
                    severity_hint=item.severity_hint or checklist_item.default_severity,
                    revision=new_revision + 1,
                    submitted_at=utc_now_iso(),
                )
                results.append(result)
            else:
                result.result_status = item.result_status
                result.measured_value = item.measured_value
                result.photo_url = item.photo_url
                result.note = item.note
                result.severity_hint = item.severity_hint or checklist_item.default_severity
                result.review_state = ReviewState.SUBMITTED
                result.revision = new_revision + 1
                result.submitted_at = utc_now_iso()
                result.returned_at = None
            outcome.accepted_items.append(item.item_code)
            outcome.results_touched.append(result)

            self._sync_hazard(task, result, hazards, item, actor_id, actor_role, outcome)

        if outcome.accepted_items:
            new_revision += 1
            task.revision = new_revision
        task.status = self.aggregate_task_status(task, results)
        if task.status == InspectionStatus.REVIEWED and not task.finished_at:
            task.finished_at = utc_now_iso()
        outcome.new_revision = new_revision

        if outcome.conflicts and outcome.accepted_items:
            outcome.state = SubmissionState.PARTIAL
            self._audit(
                actor_id, actor_role, AuditAction.SUBMISSION_PARTIAL,
                "InspectionTask", task.id,
                f"accepted={len(outcome.accepted_items)} conflicts={len(outcome.conflicts)}",
            )
        elif outcome.conflicts:
            outcome.state = SubmissionState.CONFLICT
            self._audit(
                actor_id, actor_role, AuditAction.SUBMISSION_CONFLICT,
                "InspectionTask", task.id,
                f"all {len(outcome.conflicts)} items protected",
            )
        else:
            self._audit(
                actor_id, actor_role, AuditAction.SUBMISSION_ACCEPT,
                "InspectionTask", task.id,
                f"revision={new_revision} items={len(outcome.accepted_items)}",
            )
        if outcome.accepted_items:
            self._audit(
                actor_id, actor_role, AuditAction.TASK_SUBMIT,
                "InspectionTask", task.id,
                f"client_submission_id={client_submission_id} revision={new_revision} "
                f"items={','.join(outcome.accepted_items)}",
            )
        return outcome

    @staticmethod
    def _touch_draft(result: ResultRecord, item: SubmittedItem) -> None:
        if item.measured_value:
            result.measured_value = item.measured_value
        if item.photo_url:
            result.photo_url = item.photo_url
        if item.note:
            result.note = item.note

    def _sync_hazard(
        self,
        task: TaskRecord,
        result: ResultRecord,
        hazards: list[HazardRecord],
        item: SubmittedItem,
        actor_id: int,
        actor_role: str,
        outcome: SubmissionOutcome,
    ) -> None:
        """异常→至多一张在途隐患单；恢复正常→撤销在途单。"""

        existing = self._open_hazard(hazards, result.id)
        if item.result_status == ResultStatus.ABNORMAL:
            if existing is not None:
                # 同一检查项（含同一提交重试）只保留一张在途隐患单。
                existing.severity = item.severity_hint or existing.severity
                return
            hazard = HazardRecord(
                id=self._new_id("hazard_ticket"),
                result_id=result.id,
                device_id=result.device_id,
                task_id=task.id,
                severity=item.severity_hint or result.severity_hint or HazardSeverity.MEDIUM,
                owner_id=item.owner_id or 0,
                deadline=item.deadline or "",
                rectify_status=HazardRectifyStatus.OPEN,
                item_code=result.item_code,
            )
            hazards.append(hazard)
            outcome.hazards_created.append(hazard)
            self._audit(
                actor_id, actor_role, AuditAction.HAZARD_CREATE,
                "HazardTicket", hazard.id,
                f"result={result.id} device={result.device_id} severity={hazard.severity}",
            )
        elif item.result_status == ResultStatus.NORMAL and existing is not None:
            existing.rectify_status = HazardRectifyStatus.CANCELLED
            existing.closed_at = utc_now_iso()
            existing.rectify_note = "检查项复查正常，提交链自动撤销隐患单"
            outcome.hazards_cancelled.append(existing)
            self._audit(
                actor_id, actor_role, AuditAction.HAZARD_AUTO_CANCEL,
                "HazardTicket", existing.id, f"result={result.id} returned normal",
            )

    # --------------------------------------------------------------- review

    def review_results(
        self,
        task: TaskRecord,
        results: list[ResultRecord],
        decision: str,
        item_codes: list[str],
        note: str,
        actor_id: int,
        actor_role: str,
    ) -> dict:
        self._require_role(actor_role, (UserRole.SUPERVISOR,))
        if decision not in (ReviewDecision.APPROVE, ReviewDecision.RETURN):
            raise errors.ValidationChainError(f"bad decision {decision}")
        if not item_codes:
            raise errors.ValidationChainError("review must name item_codes")

        touched: list[ResultRecord] = []
        for code in item_codes:
            result = self._active_result(results, task.id, code)
            if result is None:
                raise errors.ReviewTargetError(details={"item_code": code, "review_state": None})
            if decision == ReviewDecision.APPROVE:
                if result.review_state != ReviewState.SUBMITTED:
                    raise errors.ReviewTargetError(
                        details={"item_code": code, "review_state": result.review_state},
                    )
                result.review_state = ReviewState.REVIEWED
                result.reviewed_at = utc_now_iso()
                self._audit(
                    actor_id, actor_role, AuditAction.RESULT_REVIEW_APPROVE,
                    "InspectionResult", result.id, f"item={code} note={note}",
                )
            else:
                # 复核退回可作用于 SUBMITTED；对 REVIEWED 的退回视为“重开”，
                # 均只放开被点名检查项，其余结果保持原状。
                if result.review_state not in (ReviewState.SUBMITTED, ReviewState.REVIEWED):
                    raise errors.ReviewTargetError(
                        details={"item_code": code, "review_state": result.review_state},
                    )
                result.review_state = ReviewState.RETURNED
                result.returned_at = utc_now_iso()
                result.reviewed_at = None
                self._audit(
                    actor_id, actor_role, AuditAction.RESULT_REVIEW_RETURN,
                    "InspectionResult", result.id, f"item={code} note={note}",
                )
            touched.append(result)

        if decision == ReviewDecision.RETURN:
            task.revision += 1
            self._audit(
                actor_id, actor_role, AuditAction.TASK_REVISION_BUMP,
                "InspectionTask", task.id, f"revision={task.revision} reason=review_return",
            )
        task.status = self.aggregate_task_status(task, results)
        if task.status == InspectionStatus.REVIEWED:
            task.finished_at = utc_now_iso()
        return {
            "decision": decision,
            "item_codes": item_codes,
            "new_revision": task.revision,
            "task_status": task.status,
            "results_touched": touched,
        }

    # ------------------------------------------------------ checklist change

    def change_checklist(
        self,
        task: TaskRecord,
        results: list[ResultRecord],
        hazards: list[HazardRecord],
        changes: ChecklistChanges,
        actor_id: int,
        actor_role: str,
    ) -> dict:
        self._require_role(actor_role, (UserRole.SUPERVISOR,))
        discarded: list[ResultRecord] = []
        cancelled: list[HazardRecord] = []
        added: list[ChecklistItemRecord] = []

        for code in changes.removed:
            item = self._active_item(task, code)
            if item is None:
                raise errors.ChecklistItemError(details={"item_code": code})
            item.active = False
            result = self._active_result(results, task.id, code)
            if result is not None:
                result.review_state = ReviewState.DISCARDED
                discarded.append(result)
                self._audit(
                    actor_id, actor_role, AuditAction.RESULT_DISCARD,
                    "InspectionResult", result.id, f"item={code} removed from checklist",
                )
                hazard = self._open_hazard(hazards, result.id)
                if hazard is not None:
                    hazard.rectify_status = HazardRectifyStatus.CANCELLED
                    hazard.closed_at = utc_now_iso()
                    hazard.rectify_note = "检查项被删除，隐患单随检查链撤销"
                    cancelled.append(hazard)
                    self._audit(
                        actor_id, actor_role, AuditAction.HAZARD_AUTO_CANCEL,
                        "HazardTicket", hazard.id, f"item={code} discarded",
                    )

        existing_codes = {i.item_code: i for i in task.checklist_items}
        for item in changes.added:
            if not item.item_code or item.device_id <= 0:
                raise errors.ChecklistItemError(details={"item_code": item.item_code})
            if item.item_code in existing_codes and existing_codes[item.item_code].active:
                raise errors.ChecklistItemError(
                    f"item {item.item_code} already exists", details={"item_code": item.item_code},
                )
            item.active = True
            task.checklist_items.append(item)
            added.append(item)
            results.append(
                ResultRecord(
                    id=self._new_id("inspection_result"),
                    task_id=task.id,
                    device_id=item.device_id,
                    item_code=item.item_code,
                    result_status=ResultStatus.PENDING,
                    review_state=ReviewState.DRAFT,
                    severity_hint=item.default_severity,
                )
            )

        for patch in changes.updated:
            code = patch.get("item_code")
            item = self._active_item(task, code) if code else None
            if item is None:
                raise errors.ChecklistItemError(details={"item_code": code})
            if patch.get("title"):
                item.title = patch["title"]
            new_severity = patch.get("default_severity")
            if new_severity:
                if new_severity not in HazardSeverity.ALL:
                    raise errors.ChecklistItemError(details={"item_code": code, "severity": new_severity})
                item.default_severity = new_severity
                result = self._active_result(results, task.id, code)
                if result is not None:
                    result.severity_hint = new_severity
                    hazard = self._open_hazard(hazards, result.id)
                    # 检查项修改后隐患重判：在途单沿用新等级，设备状态随之重算。
                    if hazard is not None:
                        hazard.severity = new_severity

        if not (added or changes.removed or changes.updated):
            raise errors.ChecklistItemError("no checklist changes supplied")

        task.revision += 1
        task.status = self.aggregate_task_status(task, results)
        self._audit(
            actor_id, actor_role, AuditAction.TASK_CHECKLIST_CHANGE,
            "InspectionTask", task.id,
            f"added={len(added)} removed={len(changes.removed)} updated={len(changes.updated)} "
            f"revision={task.revision}",
        )
        return {
            "added": added,
            "discarded": discarded,
            "cancelled_hazards": cancelled,
            "new_revision": task.revision,
            "task_status": task.status,
        }

    # ------------------------------------------------------------ hazard flow

    def assign_hazard(self, hazard: HazardRecord, owner_id: int,
                      actor_id: int, actor_role: str) -> HazardRecord:
        self._require_role(actor_role, (UserRole.SUPERVISOR,))
        if hazard.rectify_status not in HazardRectifyStatus.OPEN_LIKE:
            raise errors.HazardStateError(details={"hazard_id": hazard.id, "status": hazard.rectify_status})
        hazard.owner_id = owner_id
        self._audit(
            actor_id, actor_role, AuditAction.HAZARD_CREATE,
            "HazardTicket", hazard.id, f"assigned owner={owner_id}",
        )
        return hazard

    def rectify_hazard(self, hazard: HazardRecord, note: str,
                       actor_id: int, actor_role: str) -> HazardRecord:
        self._require_role(actor_role, (UserRole.MAINTAINER,))
        if hazard.rectify_status != HazardRectifyStatus.OPEN:
            raise errors.HazardStateError(details={"hazard_id": hazard.id, "status": hazard.rectify_status})
        hazard.rectify_status = HazardRectifyStatus.RECTIFIED
        hazard.rectify_note = note
        self._audit(
            actor_id, actor_role, AuditAction.HAZARD_RECTIFY,
            "HazardTicket", hazard.id, note[:200],
        )
        return hazard

    def verify_hazard(self, hazard: HazardRecord, approved: bool, note: str,
                      actor_id: int, actor_role: str) -> HazardRecord:
        self._require_role(actor_role, (UserRole.SUPERVISOR,))
        if hazard.rectify_status not in HazardRectifyStatus.OPEN_LIKE:
            raise errors.HazardStateError(details={"hazard_id": hazard.id, "status": hazard.rectify_status})
        if approved:
            hazard.rectify_status = HazardRectifyStatus.CLOSED
            hazard.closed_at = utc_now_iso()
            hazard.rectify_note = (hazard.rectify_note + " | " if hazard.rectify_note else "") + note
            action = AuditAction.HAZARD_VERIFY_CLOSE
        else:
            hazard.rectify_status = HazardRectifyStatus.OPEN
            hazard.rectify_note = (hazard.rectify_note + " | 复验退回: " if hazard.rectify_note else "复验退回: ") + note
            action = AuditAction.HAZARD_RECTIFY
        self._audit(
            actor_id, actor_role, action, "HazardTicket", hazard.id,
            f"approved={approved} {note[:180]}",
        )
        return hazard
