import { useCallback, useEffect, useMemo, useState } from "react";
import {
  changeChecklist,
  listConflictZone,
  listInspectionTask,
  reviewTask,
} from "../api/InspectionTask";
import { ApiError, newSubmissionId } from "../api/client";
import { ChecklistPanel } from "../components/common/ChecklistPanel";
import { StatusBadge } from "../components/common/StatusBadge";
import { ConflictReasonText } from "../constants/DeviceCompliance";
import { ResultStatus } from "../constants/ResultStatus";
import { InspectionStatusText } from "../constants/InspectionStatus";
import { useAuthStore } from "../stores/AuthStore";
import { can } from "../utils/permissions";
import type { SubmissionConflict } from "../types/Chain";
import type { InspectionTask } from "../types/InspectionTask";
import type { SubmitItem } from "../types/InspectionResult";
import { useChecklistProgress } from "../hooks/useChecklistProgress";
import { useReviewChain } from "../hooks/useReviewChain";

export function TasksPage() {
  const user = useAuthStore((s) => s.user);
  const [tasks, setTasks] = useState<InspectionTask[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [draft, setDraft] = useState<Record<string, "PENDING" | "NORMAL" | "ABNORMAL">>({});
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [submissionId, setSubmissionId] = useState<string>(() => newSubmissionId());
  const [message, setMessage] = useState("");
  const [conflicts, setConflicts] = useState<SubmissionConflict[]>([]);

  const { task, loading, lastOutcome, error, refresh, submit } =
    useReviewChain(selectedId ?? 0);
  const progress = useChecklistProgress(task);

  const loadTasks = useCallback(async () => {
    const rows = await listInspectionTask();
    setTasks(rows);
    if (rows.length && selectedId === null) setSelectedId(rows[0].id);
  }, [selectedId]);

  useEffect(() => {
    void loadTasks().catch(() => undefined);
  }, [loadTasks]);

  useEffect(() => {
    if (selectedId === null) return;
    void refresh();
    void listConflictZone(selectedId).then(setConflicts).catch(() => undefined);
  }, [selectedId, refresh]);

  // 选中任务后用服务端结果初始化本地草稿
  useEffect(() => {
    if (!task) return;
    setDraft(
      Object.fromEntries(
        task.results.map((r) => [r.item_code, r.result_status as "PENDING" | "NORMAL" | "ABNORMAL"]),
      ),
    );
    setNotes(Object.fromEntries(task.results.map((r) => [r.item_code, r.note ?? ""])));
  }, [task]);

  const draftItems: SubmitItem[] = useMemo(() => {
    if (!task) return [];
    return task.checklist_items
      .filter((item) => item.active)
      .map((item) => ({
        item_code: item.item_code,
        result_status: draft[item.item_code] ?? ResultStatus.PENDING,
        measured_value: notes[item.item_code] ?? "",
        note: notes[item.item_code] ?? "",
        severity_hint: item.default_severity,
      }));
  }, [task, draft, notes]);

  const toggle = (code: string) => {
    setDraft((prev) => {
      const current = prev[code] ?? ResultStatus.PENDING;
      const next =
        current === ResultStatus.PENDING
          ? ResultStatus.ABNORMAL
          : current === ResultStatus.ABNORMAL
            ? ResultStatus.NORMAL
            : ResultStatus.PENDING;
      return { ...prev, [code]: next };
    });
  };

  const onSubmit = async () => {
    setMessage("");
    try {
      // 复用 submissionId：同一提交重试只生成一张隐患单
      const { outcome } = await submit(draftItems, submissionId);
      setMessage(
        outcome.state === "PARTIAL"
          ? "部分受理：已复核项保持锁定，其余检查项已提交"
          : outcome.state === "CONFLICT"
            ? "全部检查项已复核锁定，未发生覆盖"
            : "提交成功，异常检查项已进入隐患整改链",
      );
      await listConflictZone(selectedId ?? 0).then(setConflicts);
      await loadTasks();
    } catch (err) {
      if (err instanceof ApiError && err.code === "STALE_TASK_REVISION") {
        setMessage(`修订号过期（当前修订 ${err.details.current_revision}），本次提交已进入冲突区，未覆盖任何结果。请刷新完整任务后重试。`);
      } else if (err instanceof ApiError) {
        setMessage(err.message);
      }
      await listConflictZone(selectedId ?? 0).then(setConflicts).catch(() => undefined);
    }
  };

  const onReview = async (decision: "APPROVE" | "RETURN") => {
    if (!task || !selectedId) return;
    const submittedCodes = task.results
      .filter((r) => r.review_state === "SUBMITTED")
      .map((r) => r.item_code);
    if (decision === "RETURN") {
      // 退回只点名当前勾选项；这里默认全部待复核项，可按需单选
      const picked = window.prompt(
        "输入要退回（只放开这些检查项）的检查项编码，逗号分隔",
        submittedCodes.join(","),
      );
      if (picked === null) return;
      const codes = picked.split(",").map((s) => s.trim()).filter(Boolean);
      await reviewTask(selectedId, { decision: "RETURN", item_codes: codes, note: "复核退回" });
    } else {
      await reviewTask(selectedId, { decision: "APPROVE", item_codes: submittedCodes, note: "复核通过" });
    }
    setMessage(decision === "RETURN" ? "已退回：仅被点名检查项放开" : "已复核通过");
    await refresh();
    await loadTasks();
  };

  const onAddItem = async () => {
    if (!selectedId) return;
    const code = window.prompt("新检查项编码 item_code");
    const deviceId = Number(window.prompt("关联设备 ID"));
    if (!code || !deviceId) return;
    try {
      await changeChecklist(selectedId, {
        added: [{ item_code: code, device_id: deviceId, title: code, default_severity: "MEDIUM" }],
      });
      setMessage("检查项已新增：任务修订号自增，设备/隐患状态已重算");
      await refresh();
      await loadTasks();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "操作失败");
    }
  };

  const returnedCodes = useMemo(
    () => task?.results.filter((r) => r.review_state === "RETURNED").map((r) => r.item_code) ?? [],
    [task],
  );

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">fire-inspect · 复核链</p>
          <h1>巡检任务</h1>
        </div>
        {task && <StatusBadge value={task.status} />}
      </header>

      {message && <div className="banner info">{message}</div>}
      {error && <div className="banner danger">{error.message}</div>}

      <section className="panel">
        <div className="filter-bar">
          <label>
            任务
            <select value={selectedId ?? ""} onChange={(e) => setSelectedId(Number(e.target.value))}>
              {tasks.map((t) => (
                <option key={t.id} value={t.id}>
                  #{t.id} rev.{t.revision} · {InspectionStatusText[t.status as keyof typeof InspectionStatusText] ?? t.status}
                </option>
              ))}
            </select>
          </label>
          <span className="muted">修订号：{task?.revision ?? "-"} · 复核进度 {progress.reviewed}/{progress.total}（{progress.percent}%）</span>
        </div>
      </section>

      {task && (
        <>
          <section className="panel wide">
            <h2>完整检查单（断网恢复后续传仍基于此修订号）</h2>
            <ChecklistPanel
              task={task}
              editableResultStatusByCode={draft}
              onToggleResult={toggle}
              onNoteChange={(code, note) => setNotes((p) => ({ ...p, [code]: note }))}
              readonly={!can(user?.role, "submitInspection")}
              highlightCodes={returnedCodes}
            />
            <div className="actions">
              {can(user?.role, "submitInspection") && (
                <button type="button" className="primary" disabled={loading} onClick={onSubmit}>
                  提交（携带 rev.{task.revision}）
                </button>
              )}
              {can(user?.role, "reviewInspection") && (
                <>
                  <button type="button" onClick={() => void onReview("APPROVE")}>复核通过</button>
                  <button type="button" onClick={() => void onReview("RETURN")}>退回点名项</button>
                  <button type="button" onClick={() => void onAddItem()}>修改检查项</button>
                </>
              )}
              <button
                type="button"
                onClick={() => {
                  setSubmissionId(newSubmissionId());
                  setMessage("已生成新的提交幂等键（旧提交重试时请保持不变）");
                }}
              >
                换新提交ID
              </button>
            </div>
            {lastOutcome && (
              <p className="muted small">
                上次提交：{lastOutcome.state}，修订 {lastOutcome.base_revision} → {lastOutcome.new_revision}，
                生成隐患 {lastOutcome.hazard_ids_created.length} 张，
                {lastOutcome.replayed ? "本次为重试回放" : "首次受理"}
              </p>
            )}
          </section>

          <section className="panel wide">
            <h2>提交冲突区</h2>
            {conflicts.length === 0 ? (
              <p className="empty">暂无冲突提交</p>
            ) : (
              conflicts.map((c) => (
                <article className="row" key={c.id}>
                  <strong>{c.client_submission_id}</strong>
                  <span className="muted">
                    基于 rev.{c.base_revision}，当前 rev.{c.current_revision}
                  </span>
                  <StatusBadge value={c.reason === "STALE_TASK_REVISION" ? "OVERDUE" : "RETURNED"} />
                  <span>{ConflictReasonText[c.reason as keyof typeof ConflictReasonText] ?? c.reason}</span>
                </article>
              ))
            )}
          </section>
        </>
      )}
    </section>
  );
}
