import { useEffect, useState } from "react";
import { listAuditLogs } from "../api/Compliance";
import { ApiError } from "../api/client";
import type { AuditLogEntry } from "../types/Chain";

/** 审计页（审计员/主管可见）：任务重开后仍能追到结果、隐患与审计记录。 */
export function AuditPage() {
  const [rows, setRows] = useState<AuditLogEntry[]>([]);
  const [targetType, setTargetType] = useState("");
  const [targetId, setTargetId] = useState("");
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setRows(
        await listAuditLogs({
          target_type: targetType || undefined,
          target_id: targetId || undefined,
        }),
      );
      setError("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "加载失败");
    }
  };

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">fire-inspect · 审计</p>
          <h1>操作审计日志</h1>
        </div>
      </header>
      {error && <div className="banner danger">{error}</div>}

      <section className="panel">
        <div className="filter-bar">
          <label>
            目标类型
            <select value={targetType} onChange={(e) => setTargetType(e.target.value)}>
              <option value="">全部</option>
              <option value="InspectionTask">巡检任务</option>
              <option value="InspectionResult">巡检结果</option>
              <option value="HazardTicket">隐患单</option>
              <option value="FireDevice">消防设备</option>
            </select>
          </label>
          <label>
            目标 ID
            <input value={targetId} onChange={(e) => setTargetId(e.target.value)} placeholder="如 1" />
          </label>
          <button type="button" className="primary" onClick={() => void load()}>查询</button>
        </div>
      </section>

      <section className="panel wide">
        <div className="table">
          <article className="row head">
            <span>时间</span>
            <span>操作人</span>
            <span>动作</span>
            <span>对象</span>
            <span>详情</span>
          </article>
          {rows.map((log) => (
            <article className="row" key={log.id}>
              <span className="muted small">{log.created_at}</span>
              <span>#{log.actor_id} {log.actor_role}</span>
              <strong>{log.action}</strong>
              <span>{log.target_type}#{log.target_id}</span>
              <span className="muted small">{log.detail}</span>
            </article>
          ))}
          {rows.length === 0 && <p className="empty">暂无审计记录</p>}
        </div>
      </section>
    </section>
  );
}
