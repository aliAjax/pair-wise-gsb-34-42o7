"""复核链引擎测试（仅标准库）：python3 -m unittest backend.tests.test_review_chain -v

也可直接：python3 backend/tests/test_review_chain.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.constants.hazard_severity import HazardRectifyStatus, HazardSeverity
from src.constants.inspection_status import InspectionStatus
from src.constants.result_status import ResultStatus
from src.constants.review_state import ReviewState
from src.constants.submission_conflict import ConflictReason, SubmissionState
from src.constants.user_role import UserRole
from src.domain import errors
from src.domain.compliance import building_compliance_rate, recompute_device_compliance
from src.domain.records import (
    ChecklistItemRecord,
    DeviceRecord,
    HazardRecord,
    TaskRecord,
)
from src.domain.review_chain_engine import (
    ChecklistChanges,
    IdProvider,
    ReviewChainEngine,
    SubmittedItem,
)


def make_task(revision=1):
    return TaskRecord(
        id=10,
        building_id=1,
        inspector_id=100,
        plan_date="2026-10-03",
        task_type="HYDRANT",
        status=InspectionStatus.PLANNED,
        checklist_version="v1",
        revision=revision,
        checklist_items=[
            ChecklistItemRecord(item_code="CHK-1", device_id=1, title="压力", default_severity=HazardSeverity.HIGH),
            ChecklistItemRecord(item_code="CHK-2", device_id=2, title="外观", default_severity=HazardSeverity.MEDIUM),
            ChecklistItemRecord(item_code="CHK-3", device_id=3, title="标识", default_severity=HazardSeverity.LOW),
        ],
    )


def make_device(device_id, status="NORMAL"):
    return DeviceRecord(
        id=device_id, building_id=1, device_code=f"D{device_id}", device_type="HYDRANT",
        floor="1", location_desc="x", install_date="2025-01-01", status=status,
    )


class ReviewChainTest(unittest.TestCase):
    def setUp(self):
        self.engine = ReviewChainEngine(IdProvider(1))
        self.results = []
        self.hazards = []

    def submit(self, task, base_revision, items, actor_id=100, role=UserRole.INSPECTOR, sid="s1"):
        return self.engine.submit_results(
            task, self.results, self.hazards, base_revision, items,
            actor_id, role, sid,
        )

    # 1. 正常提交：异常项各生成一张隐患单，任务进 SUBMITTED，修订号 +1
    def test_full_submit_creates_hazards_and_bumps_revision(self):
        task = make_task()
        outcome = self.submit(task, 1, [
            SubmittedItem("CHK-1", ResultStatus.ABNORMAL, measured_value="0.2MPa"),
            SubmittedItem("CHK-2", ResultStatus.NORMAL, measured_value="ok"),
            SubmittedItem("CHK-3", ResultStatus.NORMAL, measured_value="ok"),
        ])
        self.assertEqual(outcome.state, SubmissionState.ACCEPTED)
        self.assertEqual(len(outcome.hazards_created), 1)
        self.assertEqual(task.revision, 2)
        self.assertEqual(task.status, InspectionStatus.SUBMITTED)
        hazard = self.hazards[0]
        self.assertEqual(hazard.severity, HazardSeverity.HIGH)
        self.assertEqual(hazard.device_id, 1)

    # 2. 旧修订号：整包进冲突区，不覆盖任何结果
    def test_stale_revision_enters_conflict_zone(self):
        task = make_task()
        self.submit(task, 1, [SubmittedItem("CHK-1", ResultStatus.ABNORMAL)], sid="a")
        before = list(self.results)
        with self.assertRaises(errors.StaleRevisionError) as ctx:
            self.submit(task, 1, [SubmittedItem("CHK-2", ResultStatus.ABNORMAL)], sid="b")
        self.assertEqual(ctx.exception.details["current_revision"], 2)
        self.assertEqual(len(self.engine.conflicts), 1)
        self.assertEqual(self.engine.conflicts[0].reason, ConflictReason.STALE_TASK_REVISION)
        # 现有结果一条未变
        self.assertEqual(self.results, before)
        self.assertEqual(len(self.hazards), 1)

    # 3. 已复核结果不可被覆盖：当前修订下逐项保护，其余项正常受理
    def test_reviewed_result_protected_others_accepted(self):
        task = make_task()
        self.submit(task, 1, [
            SubmittedItem("CHK-1", ResultStatus.NORMAL),
            SubmittedItem("CHK-2", ResultStatus.NORMAL),
        ])
        self.engine.review_results(
            task, self.results, "APPROVE", ["CHK-1"], "ok", 9, UserRole.SUPERVISOR,
        )
        r1 = next(r for r in self.results if r.item_code == "CHK-1")
        reviewed_revision = r1.revision
        # 重开场景：当前修订（3）提交，CHK-1 已复核被保护，CHK-2 被接受
        outcome = self.submit(task, task.revision, [
            SubmittedItem("CHK-1", ResultStatus.ABNORMAL),
            SubmittedItem("CHK-2", ResultStatus.ABNORMAL),
        ], sid="retry")
        self.assertEqual(outcome.state, SubmissionState.PARTIAL)
        self.assertEqual(len(outcome.accepted_items), 1)
        self.assertEqual(outcome.conflicts[0]["reason"], ConflictReason.REVIEWED_PROTECTED)
        r1_after = next(r for r in self.results if r.item_code == "CHK-1")
        self.assertEqual(r1_after.result_status, ResultStatus.NORMAL)
        self.assertEqual(r1_after.review_state, ReviewState.REVIEWED)
        self.assertEqual(r1_after.revision, reviewed_revision)
        # 仅 CHK-2 生成隐患
        self.assertEqual(len(self.hazards), 1)
        self.assertEqual(self.hazards[0].device_id, 2)

    # 4. 同一提交重试：一个结果至多一张在途隐患单
    def test_retry_same_submission_single_hazard(self):
        task = make_task()
        self.submit(task, 1, [SubmittedItem("CHK-1", ResultStatus.ABNORMAL)], sid="same-id")
        self.assertEqual(len(self.hazards), 1)
        # 模拟 service 未拦截、引擎再次被调用（同修订号、同内容）
        outcome = self.submit(task, task.revision, [
            SubmittedItem("CHK-1", ResultStatus.ABNORMAL, measured_value="0.3MPa"),
        ], sid="same-id")
        self.assertEqual(len(outcome.hazards_created), 0)
        self.assertEqual(len([h for h in self.hazards if h.rectify_status in HazardRectifyStatus.OPEN_LIKE]), 1)

    # 5. 检查项修改后：废弃结果、重判隐患、修订号增加
    def test_checklist_change_recalculates_hazard(self):
        task = make_task()
        self.submit(task, 1, [
            SubmittedItem("CHK-1", ResultStatus.ABNORMAL),
            SubmittedItem("CHK-2", ResultStatus.ABNORMAL),
        ])
        self.assertEqual(len(self.hazards), 2)
        # 删除 CHK-2 → 结果 DISCARDED，隐患 CANCELLED；CHK-1 降级为 LOW
        changes = ChecklistChanges(
            removed=["CHK-2"],
            updated=[{"item_code": "CHK-1", "default_severity": HazardSeverity.LOW}],
            added=[ChecklistItemRecord(item_code="CHK-4", device_id=4, title="新增项", default_severity="MEDIUM")],
        )
        result = self.engine.change_checklist(task, self.results, self.hazards, changes, 9, UserRole.SUPERVISOR)
        self.assertEqual(result["new_revision"], 3)
        discarded = next(r for r in self.results if r.item_code == "CHK-2")
        self.assertEqual(discarded.review_state, ReviewState.DISCARDED)
        cancelled = next(h for h in self.hazards if h.device_id == 2)
        self.assertEqual(cancelled.rectify_status, HazardRectifyStatus.CANCELLED)
        high_hazard = next(h for h in self.hazards if h.device_id == 1)
        self.assertEqual(high_hazard.severity, HazardSeverity.LOW)
        draft = next(r for r in self.results if r.item_code == "CHK-4")
        self.assertEqual(draft.review_state, ReviewState.DRAFT)
        # 非主管不允许改检查项
        with self.assertRaises(errors.RbacDeniedError):
            self.engine.change_checklist(
                task, self.results, self.hazards,
                ChecklistChanges(removed=["CHK-1"]), 100, UserRole.INSPECTOR,
            )

    # 6. 复核退回只放开点名项，其余结果原状不动
    def test_return_opens_only_named_items(self):
        task = make_task()
        self.submit(task, 1, [
            SubmittedItem("CHK-1", ResultStatus.ABNORMAL),
            SubmittedItem("CHK-2", ResultStatus.NORMAL),
        ])
        self.engine.review_results(
            task, self.results, "APPROVE", ["CHK-2"], "ok", 9, UserRole.SUPERVISOR,
        )
        result = self.engine.review_results(
            task, self.results, "RETURN", ["CHK-1"], "照片不清", 9, UserRole.SUPERVISOR,
        )
        self.assertEqual(task.status, InspectionStatus.RETURNED)
        self.assertGreater(result["new_revision"], 2)
        r1 = next(r for r in self.results if r.item_code == "CHK-1")
        r2 = next(r for r in self.results if r.item_code == "CHK-2")
        self.assertEqual(r1.review_state, ReviewState.RETURNED)
        self.assertEqual(r2.review_state, ReviewState.REVIEWED)
        # 未提交的检查项不能退回
        with self.assertRaises(errors.ReviewTargetError):
            self.engine.review_results(
                task, self.results, "RETURN", ["CHK-3"], "x", 9, UserRole.SUPERVISOR,
            )
        # 已复核项可被重开：只影响 CHK-2
        reopen = self.engine.review_results(
            task, self.results, "RETURN", ["CHK-2"], "抽检重开", 9, UserRole.SUPERVISOR,
        )
        self.assertEqual(reopen["decision"], "RETURN")
        self.assertEqual(next(r for r in self.results if r.item_code == "CHK-2").review_state,
                         ReviewState.RETURNED)

    # 7. 未关闭高危隐患：设备台账与报表不得显示正常
    def test_open_high_hazard_blocks_normal_display(self):
        device = make_device(1)
        hazard = HazardRecord(
            id=1, result_id=1, device_id=1, task_id=10,
            severity=HazardSeverity.CRITICAL, owner_id=5, deadline="2026-10-10",
            rectify_status=HazardRectifyStatus.OPEN,
        )
        self.assertEqual(recompute_device_compliance(device, [hazard]), "HIGH_HAZARD_BLOCKED")
        rate = building_compliance_rate([device, make_device(2)], [hazard])
        self.assertEqual(rate["device_blocked"], 1)
        self.assertEqual(rate["device_normal"], 1)
        # 维保商整改后（RECTIFIED 仍未关闭）依旧封锁；主管复验关闭后恢复
        self.engine.rectify_hazard(hazard, "已更换", 5, UserRole.MAINTAINER)
        self.assertEqual(recompute_device_compliance(device, [hazard]), "HIGH_HAZARD_BLOCKED")
        self.engine.verify_hazard(hazard, True, "复验合格", 9, UserRole.SUPERVISOR)
        self.assertEqual(recompute_device_compliance(device, [hazard]), "ACTIVE")

    # 8. 权限隔离
    def test_rbac_isolation(self):
        task = make_task()
        # 维保商不能提交巡检结果
        with self.assertRaises(errors.RbacDeniedError):
            self.submit(task, 1, [SubmittedItem("CHK-1", ResultStatus.NORMAL)],
                        actor_id=5, role=UserRole.MAINTAINER, sid="x")
        # 别的巡检员不能提交
        with self.assertRaises(errors.RbacDeniedError):
            self.submit(task, 1, [SubmittedItem("CHK-1", ResultStatus.NORMAL)],
                        actor_id=101, role=UserRole.INSPECTOR, sid="y")
        # 审计员只读
        with self.assertRaises(errors.RbacDeniedError):
            self.engine.review_results(task, self.results, "APPROVE", ["CHK-1"], "", 7, UserRole.AUDITOR)

    # 9. 异常恢复正常后自动撤销隐患单
    def test_return_to_normal_cancels_hazard(self):
        task = make_task()
        self.submit(task, 1, [SubmittedItem("CHK-1", ResultStatus.ABNORMAL)], sid="ab")
        self.engine.review_results(
            task, self.results, "RETURN", ["CHK-1"], "重测", 9, UserRole.SUPERVISOR,
        )
        self.submit(task, task.revision, [SubmittedItem("CHK-1", ResultStatus.NORMAL)], sid="ok")
        hazard = self.hazards[0]
        self.assertEqual(hazard.rectify_status, HazardRectifyStatus.CANCELLED)
        self.assertIsNotNone(hazard.closed_at)
        self.assertEqual(recompute_device_compliance(make_device(1), self.hazards), "ACTIVE")

    # 10. 全部复核通过 → REVIEWED 且可重开追溯
    def test_full_review_then_reopen_trace(self):
        task = make_task()
        self.submit(task, 1, [
            SubmittedItem("CHK-1", ResultStatus.NORMAL),
            SubmittedItem("CHK-2", ResultStatus.NORMAL),
            SubmittedItem("CHK-3", ResultStatus.NORMAL),
        ])
        self.engine.review_results(
            task, self.results, "APPROVE", ["CHK-1", "CHK-2", "CHK-3"], "ok", 9, UserRole.SUPERVISOR,
        )
        self.assertEqual(task.status, InspectionStatus.REVIEWED)
        self.assertIsNotNone(task.finished_at)
        actions = {e.action for e in self.engine.events}
        self.assertIn("InspectionResult.review_approve", actions)
        self.assertIn("InspectionTask.submit", actions)
        self.assertNotIn("HazardTicket.create", actions)
        # 重开：退回 CHK-1，历史审计仍在
        self.engine.review_results(
            task, self.results, "RETURN", ["CHK-1"], "需要补测", 9, UserRole.SUPERVISOR,
        )
        self.assertEqual(task.status, InspectionStatus.RETURNED)
        self.assertGreaterEqual(len(self.engine.events), 7)
        # 重开后结果链仍可追溯
        r1 = next(r for r in self.results if r.item_code == "CHK-1")
        self.assertEqual(r1.review_state, ReviewState.RETURNED)
        self.assertEqual(len({r.id for r in self.results}), len(self.results))


if __name__ == "__main__":
    unittest.main(verbosity=2)
