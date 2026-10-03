"""ChainService 编排测试：注入假仓储（不依赖 SQLAlchemy），验证幂等、冲突与落库。

运行：python3 backend/tests/test_chain_service.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.constants.review_state import ReviewState
from src.constants.user_role import UserRole
from src.domain.records import AuditEventRecord, ConflictRecord, HazardRecord, ResultRecord, TaskRecord
from src.services import chain_service as chain_service_module
from src.services.chain_service import ChainService


def _task():
    return TaskRecord(
        id=1, building_id=1, inspector_id=100, plan_date="2026-10-03",
        task_type="ROUTINE", status="PLANNED", checklist_version="v1",
        finished_at=None, revision=1,
        checklist_items=[
            _item("CHK-1", 1, "HIGH"),
            _item("CHK-2", 2, "MEDIUM"),
        ],
    )


def _item(code, device_id, severity):
    from src.domain.records import ChecklistItemRecord

    return ChecklistItemRecord(item_code=code, device_id=device_id, title=code,
                               default_severity=severity, active=True)


def _results():
    return [
        ResultRecord(id=1, task_id=1, device_id=1, item_code="CHK-1",
                     result_status="PENDING", review_state="DRAFT", severity_hint="HIGH", revision=1),
        ResultRecord(id=2, task_id=1, device_id=2, item_code="CHK-2",
                     result_status="PENDING", review_state="DRAFT", severity_hint="MEDIUM", revision=1),
    ]


class FakeRepo:
    def __init__(self, db):
        self.db = db
        self.task_row = _task()
        self.results = _results()
        self.hazards: list[HazardRecord] = []
        self.conflicts: list[ConflictRecord] = []
        self.audits: list[AuditEventRecord] = []
        self.submissions: dict[tuple, dict] = {}

    def get_task_orm(self, task_id):
        return self.task_row if self.task_row.id == task_id else None

    def get_task(self, task_id):
        return self.task_row if self.task_row.id == task_id else None

    def list_results(self, task_id):
        return [r for r in self.results if r.task_id == task_id]

    def list_all_results(self):
        return list(self.results)

    def list_hazards(self):
        return list(self.hazards)

    def get_hazard_orm(self, hazard_id):
        # service 用 orm_to_hazard 读取；FakeHazardRow 提供同名属性
        hazard = next((h for h in self.hazards if h.id == hazard_id), None)
        if hazard is None:
            return None
        return FakeHazardRow(hazard)

    def persist_task(self, task):
        self.task_row.status = task.status
        self.task_row.revision = task.revision
        self.task_row.finished_at = task.finished_at
        self.task_row.checklist_items = task.checklist_items

    def find_result_row(self, task_id, result_id):
        return next((r for r in self.results if r.task_id == task_id and r.id == result_id), None)

    def upsert_result(self, result):
        existing = self.find_result_row(result.task_id, result.id)
        if existing is None:
            result.id = max((r.id for r in self.results), default=0) + 1
            self.results.append(result)
        return result

    def upsert_hazard(self, hazard):
        if not hazard.id:
            hazard.id = max((h.id for h in self.hazards), default=0) + 1
            self.hazards.append(hazard)
        else:
            existing = next((h for h in self.hazards if h.id == hazard.id), None)
            if existing is not None and existing is not hazard:
                # 引擎改的是 orm_to_hazard 生成的副本，回写到共享记录
                existing.rectify_status = hazard.rectify_status
                existing.rectify_note = hazard.rectify_note
                existing.closed_at = hazard.closed_at
                existing.severity = hazard.severity
                existing.owner_id = hazard.owner_id
                return existing
        return hazard

    def add_conflict(self, conflict):
        conflict.id = max((c.id or 0 for c in self.conflicts), default=0) + 1
        self.conflicts.append(conflict)
        return conflict

    def add_audit_events(self, events):
        self.audits.extend(events)

    def list_conflicts(self, task_id=None):
        return list(self.conflicts)

    def list_audit_logs(self, target_id=None, target_type=None):
        return list(self.audits)

    def get_submission_record(self, task_id, client_submission_id):
        return self.submissions.get((task_id, client_submission_id))

    def save_submission_record(self, task_id, client_submission_id, inspector_id,
                               base_revision, outcome_json):
        row = FakeSubmissionRow(outcome_json)
        self.submissions[(task_id, client_submission_id)] = row
        return row


class _RowView:
    """get_hazard_orm 返回领域对象即可，service 只用它做存在性判断/再读取。"""


class FakeHazardRow:
    """伪装成 ORM 行，供 persistence_mapper.orm_to_hazard/apply 读取。"""

    def __init__(self, record: HazardRecord):
        self._record = record
        for field in (
            "id", "result_id", "device_id", "task_id", "severity", "owner_id",
            "deadline", "rectify_status", "rectify_note", "closed_at", "created_at",
        ):
            setattr(self, field, getattr(record, field))
        self.active_key = "ACTIVE" if record.rectify_status in ("OPEN", "RECTIFIED") else None

    def sync_back(self):
        record = self._record
        for field in (
            "id", "result_id", "device_id", "task_id", "severity", "owner_id",
            "deadline", "rectify_status", "rectify_note", "closed_at", "created_at",
        ):
            setattr(record, field, getattr(self, field))


class FakeSubmissionRow:
    def __init__(self, outcome_json):
        self.outcome_json = outcome_json
        self.id = None


class FakeDb:
    def __init__(self):
        self.commits = 0
        self.repo = None

    def flush(self):
        pass

    def commit(self):
        self.commits += 1

    def rollback(self):
        pass


class ChainServiceOrchestrationTest(unittest.TestCase):
    def setUp(self):
        self.db = FakeDb()
        self._original = chain_service_module.ChainRepository
        chain_service_module.ChainRepository = FakeRepo
        self.service = ChainService(self.db)
        self.repo: FakeRepo = self.service.repo

    def tearDown(self):
        chain_service_module.ChainRepository = self._original

    SUBMIT = {
        "client_submission_id": "sub-1",
        "base_revision": 1,
        "items": [
            {"item_code": "CHK-1", "result_status": "ABNORMAL", "measured_value": "0.2"},
            {"item_code": "CHK-2", "result_status": "NORMAL"},
        ],
    }

    def test_submit_persists_and_is_idempotent(self):
        out1 = self.service.submit_full_task(1, self.SUBMIT, 100, UserRole.INSPECTOR)
        self.assertEqual(out1["new_revision"], 2)
        self.assertEqual(len(out1["hazard_ids_created"]), 1)
        hazard = self.repo.hazards[0]
        self.assertEqual(hazard.result_id, 1)
        self.assertEqual(hazard.severity, "HIGH")

        out2 = self.service.submit_full_task(1, self.SUBMIT, 100, UserRole.INSPECTOR)
        self.assertTrue(out2["replayed"])
        self.assertEqual(len(self.repo.hazards), 1)
        actions = [e.action for e in self.repo.audits]
        self.assertIn("InspectionTask.submit", actions)
        self.assertIn("HazardTicket.create", actions)
        # 重试回放是只读路径，不再产生事务
        self.assertEqual(self.db.commits, 1)

    def test_stale_revision_conflict_without_result_change(self):
        self.service.submit_full_task(1, {
            "client_submission_id": "a",
            "base_revision": 1,
            "items": [{"item_code": "CHK-1", "result_status": "NORMAL"}],
        }, 100, UserRole.INSPECTOR)

        from src.domain import errors
        with self.assertRaises(errors.StaleRevisionError):
            self.service.submit_full_task(1, {
                "client_submission_id": "b",
                "base_revision": 1,
                "items": [{"item_code": "CHK-2", "result_status": "ABNORMAL"}],
            }, 100, UserRole.INSPECTOR)

        self.assertEqual(len(self.repo.conflicts), 1)
        self.assertEqual(self.repo.conflicts[0].current_revision, 2)
        chk2 = next(r for r in self.repo.results if r.item_code == "CHK-2")
        self.assertEqual(chk2.result_status, "PENDING")
        self.assertEqual(chk2.review_state, ReviewState.DRAFT)
        self.assertEqual(len(self.repo.hazards), 0)
        # 过期提交也有提交号，且冲突区可按任务查
        self.assertTrue(all(c.task_id == 1 for c in self.service.conflicts(1)))

    def test_return_opens_only_named_items_and_keeps_trace(self):
        self.service.submit_full_task(1, {
            "client_submission_id": "a",
            "base_revision": 1,
            "items": [
                {"item_code": "CHK-1", "result_status": "ABNORMAL"},
                {"item_code": "CHK-2", "result_status": "NORMAL"},
            ],
        }, 100, UserRole.INSPECTOR)
        self.service.review(
            1, {"decision": "APPROVE", "item_codes": ["CHK-1", "CHK-2"], "note": "ok"},
            9, UserRole.SUPERVISOR,
        )
        out = self.service.review(
            1, {"decision": "RETURN", "item_codes": ["CHK-2"], "note": "补测"},
            9, UserRole.SUPERVISOR,
        )
        self.assertEqual(out["new_revision"], 3)
        states = {r.item_code: r.review_state for r in self.repo.results}
        self.assertEqual(states["CHK-1"], ReviewState.REVIEWED)
        self.assertEqual(states["CHK-2"], ReviewState.RETURNED)
        actions = [e.action for e in self.repo.audits]
        self.assertIn("InspectionResult.review_return", actions)
        self.assertIn("InspectionTask.revision_bump", actions)

    def test_rectify_and_verify_close_flow(self):
        self.service.submit_full_task(1, self.SUBMIT, 100, UserRole.INSPECTOR)
        hazard_id = self.repo.hazards[0].id
        self.service.rectify_hazard(hazard_id, "已更换", 2, UserRole.MAINTAINER)
        self.assertEqual(self.repo.hazards[0].rectify_status, "RECTIFIED")
        self.service.verify_hazard(hazard_id, True, "复验合格", 9, UserRole.SUPERVISOR)
        self.assertEqual(self.repo.hazards[0].rectify_status, "CLOSED")
        self.assertIsNotNone(self.repo.hazards[0].closed_at)
        actions = [e.action for e in self.repo.audits]
        self.assertIn("HazardTicket.rectify", actions)
        self.assertIn("HazardTicket.verify_close", actions)

    def test_rbac_denied_at_service_boundary(self):
        from src.domain import errors
        with self.assertRaises(errors.RbacDeniedError):
            self.service.submit_full_task(1, self.SUBMIT, 100, UserRole.AUDITOR)
        with self.assertRaises(errors.RbacDeniedError):
            self.service.submit_full_task(1, self.SUBMIT, 100, UserRole.MAINTAINER)


if __name__ == "__main__":
    unittest.main(verbosity=2)
