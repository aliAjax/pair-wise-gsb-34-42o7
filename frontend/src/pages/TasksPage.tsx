import { useEffect, useMemo, useState } from "react";
import { useInspectionTaskStore } from "../stores/InspectionTaskStore";
import { useInspectionResultStore } from "../stores/InspectionResultStore";
import { useAuditLogStore } from "../stores/AuditLogStore";
import { useChecklistProgress } from "../hooks/useChecklistProgress";
import { ChecklistPanel } from "../components/common/ChecklistPanel";
import { StatusBadge } from "../components/common/StatusBadge";
import { TimelineList } from "../components/common/TimelineList";
import { EmptyState } from "../components/common/EmptyState";
import { ApiError, currentRole } from "../api/client";
import { can } from "../constants/roles";
import { ERROR_MESSAGES } from "../constants/errorMessages";

const SUBMITTABLE = ["PLANNED", "IN_PROGRESS", "OVERDUE"];

export function TasksPage() {
  const taskStore = useInspectionTaskStore();
  const resultStore = useInspectionResultStore();
  const auditStore = useAuditLogStore();
  const [activeId, setActiveId] = useState<number | null>(null);
  const [drafts, setDrafts] = useState<Record<string, { result_status: string; severity: string }>>({});
  const [rejectPick, setRejectPick] = useState<string[]>([]);
  const [message, setMessage] = useState("");
  const role = currentRole();

  const active = useMemo(
    () => taskStore.rows.find((row) => row.id === activeId) ?? null,
    [taskStore.rows, activeId]
  );
  const progress = useChecklistProgress(resultStore.rows, active?.status ?? "");

  useEffect(() => {
    // 断网恢复后先把本地队列里的完整任务续投，再拉取任务
    taskStore.flushPending().finally(() => taskStore.load());
  }, []);

  useEffect(() => {
    if (activeId === null) return;
    resultStore.load(activeId);
    taskStore.loadConflicts(activeId);
    auditStore.load("InspectionTask", activeId);
    setDrafts({});
    setRejectPick([]);
    setMessage("");
  }, [activeId, taskStore.rows]);

  const onDraftChange = (itemCode: string, patch: { result_status?: string; severity?: string }) =>
    setDrafts((prev) => {
      const base = prev[itemCode] ?? { result_status: "NORMAL", severity: "MEDIUM" };
      return { ...prev, [itemCode]: { ...base, ...patch } };
    });

  const submit = async () => {
    if (!active) return;
    setMessage("");
    // 同一修订号重投复用同一 submission_id：断网重试只生成一张隐患单
    const payload = {
      revision: active.revision,
      submission_id: `sub-${active.id}-r${active.revision}`,
      results: resultStore.rows.map((row) => ({
        device_id: row.device_id,
        item_code: row.item_code,
        result_status: drafts[row.item_code]?.result_status ?? row.result_status,
        measured_value: row.measured_value,
        photo_url: row.photo_url,
        note: row.note,
        severity: drafts[row.item_code]?.severity ?? "MEDIUM"
      }))
    };
    try {
      const resp = await taskStore.submit(active.id, payload);
      if (resp.queued) {
        setMessage("网络中断：完整任务已存入本地队列，恢复联网后自动续投");
      } else if (resp.replayed) {
        setMessage("该提交已处理过（幂等重放），未重复生成隐患单");
      } else {
        setMessage(`提交成功，已生成 ${resp.hazards.length} 张隐患单${resp.skipped_items.length ? `，跳过未放开项：${resp.skipped_items.join("、")}` : ""}`);
      }
      setDrafts({});
    } catch (err) {
      if (err instanceof ApiError && err.code === "REVISION_CONFLICT") {
        setMessage(ERROR_MESSAGES.REVISION_CONFLICT);
        taskStore.loadConflicts(active.id);
      } else {
        setMessage((err as Error).message);
      }
      taskStore.load();
    }
  };

  const review = async () => {
    if (!active) return;
    setMessage("");
    try {
      await taskStore.review(active.id);
      setMessage("复核通过，全部检查项已锁定");
    } catch (err) {
      setMessage((err as Error).message);
    }
  };

  const reject = async () => {
    if (!active || rejectPick.length === 0) return;
    setMessage("");
    try {
      const reopened = await taskStore.reject(active.id, rejectPick, "复核退回");
      setMessage(`已退回，仅放开检查项：${reopened.join("、")}，其余结果保持原状`);
      setRejectPick([]);
    } catch (err) {
      setMessage((err as Error).message);
    }
  };

  return <section>
    <h2>巡检任务复核链</h2>
    {taskStore.pendingCount > 0 && (
      <div className="panel">
        本地有 {taskStore.pendingCount} 个断网暂存的完整任务
        <button onClick={() => taskStore.flushPending()}>立即续投</button>
      </div>
    )}
    <div className="workbench">
      <div className="panel wide">
        <h2>任务列表</h2>
        <div className="table">
          {taskStore.rows.map((task) => <article key={task.id} className="row">
            <strong>#{task.id} · {task.task_type}</strong>
            <span>修订号 v{task.revision}</span>
            <StatusBadge value={task.status} />
            <button onClick={() => setActiveId(task.id)}>进入</button>
          </article>)}
        </div>
      </div>
      <div className="panel">
        <h2>说明</h2>
        <p>提交带任务修订号；旧修订进冲突区，不能覆盖已复核结果；同一提交重试只生成一张隐患单。</p>
      </div>
    </div>
    {active && (
      <div className="panel wide">
        <h2>任务 #{active.id} 检查项（修订号 v{active.revision} · {active.status}）</h2>
        <p>共 {progress.total} 项 · 已提交 {progress.submitted} · 已复核 {progress.reviewed} · 退回重开 {progress.reopened}</p>
        <ChecklistPanel
          results={resultStore.rows}
          isItemEditable={progress.isItemEditable}
          drafts={drafts}
          onDraftChange={onDraftChange} />
        <div className="actions">
          {can(role, "task:submit") && SUBMITTABLE.includes(active.status) && (
            <button onClick={submit}>提交复核（整包 v{active.revision}）</button>
          )}
          {can(role, "task:review") && active.status === "SUBMITTED" && (
            <button onClick={review}>复核通过</button>
          )}
          {can(role, "task:reject") && active.status === "SUBMITTED" && (
            <>
              <div className="table">
                {resultStore.rows.map((row) => <label key={row.id} className="row">
                  <input
                    type="checkbox"
                    checked={rejectPick.includes(row.item_code)}
                    onChange={(e) => setRejectPick((prev) =>
                      e.target.checked ? [...prev, row.item_code] : prev.filter((code) => code !== row.item_code))} />
                  <strong>{row.item_code}</strong>
                  <StatusBadge value={row.review_state} />
                </label>)}
              </div>
              <button onClick={reject} disabled={rejectPick.length === 0}>退回点名项（{rejectPick.length}）</button>
            </>
          )}
        </div>
        {message && <p className="message">{message}</p>}
        <h2>冲突区（旧修订留档，不覆盖已复核结果）</h2>
        {taskStore.conflicts.length === 0 ? <EmptyState title="暂无冲突" /> : (
          <div className="table">
            {taskStore.conflicts.map((row) => <article key={row.id} className="row">
              <strong>{row.submission_id}</strong>
              <span>提交 v{row.revision} / 当前 v{row.current_revision}</span>
              <StatusBadge value={row.reason} />
            </article>)}
          </div>
        )}
        <h2>审计记录</h2>
        {auditStore.error ? <EmptyState title={auditStore.error} /> : (
          <TimelineList items={auditStore.rows.map((row) => ({
            id: row.id,
            title: row.action,
            detail: `${row.role} · ${row.detail}`,
            time: row.created_at
          }))} />
        )}
      </div>
    )}
  </section>;
}
