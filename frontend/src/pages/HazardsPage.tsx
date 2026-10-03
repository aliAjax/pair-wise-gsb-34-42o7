import { useCallback, useEffect, useState } from "react";
import { listHazards } from "../api/HazardTicket";
import { ApiError } from "../api/client";
import { StatusBadge } from "../components/common/StatusBadge";
import { HazardSeverityTag } from "../components/common/HazardSeverityTag";
import { HazardRectifyStatus, OPEN_LIKE, type HazardRectifyStatus as HStatus } from "../constants/HazardRectifyStatus";
import { HIGH_RISK, type HazardSeverity } from "../constants/HazardSeverity";
import { useAuthStore } from "../stores/AuthStore";
import { can } from "../utils/permissions";
import type { HazardTicket } from "../types/HazardTicket";
import { useHazardFlow } from "../hooks/useHazardFlow";

const FILTERS = [
  { label: "全部", value: "" },
  { label: "待整改", value: HazardRectifyStatus.OPEN },
  { label: "待复验", value: HazardRectifyStatus.RECTIFIED },
  { label: "已关闭", value: HazardRectifyStatus.CLOSED },
  { label: "已撤销", value: HazardRectifyStatus.CANCELLED },
];

export function HazardsPage() {
  const user = useAuthStore((s) => s.user);
  const [rows, setRows] = useState<HazardTicket[]>([]);
  const [filter, setFilter] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setRows(await listHazards(filter ? { status: filter } : undefined));
  }, [filter]);

  useEffect(() => {
    void load().catch(() => undefined);
  }, [load]);

  const flow = useHazardFlow(() => void load());

  const onAssign = async (hazard: HazardTicket) => {
    const ownerId = Number(window.prompt("指派维保商用户 ID", String(hazard.owner_id || 2)));
    if (!ownerId) return;
    try {
      await flow.assign(hazard.id, ownerId);
      setNotice(`隐患 #${hazard.id} 已派单`);
    } catch (err) {
      setNotice(err instanceof ApiError ? err.message : "派单失败");
    }
  };

  const onRectify = async (hazard: HazardTicket) => {
    const note = window.prompt("整改说明", hazard.rectify_note || "已完成现场整改");
    if (note === null) return;
    try {
      await flow.rectify(hazard.id, note);
      setNotice(`隐患 #${hazard.id} 已提交整改，等待复验`);
    } catch (err) {
      setNotice(err instanceof ApiError ? err.message : "整改失败");
    }
  };

  const onVerify = async (hazard: HazardTicket, approved: boolean) => {
    const note = window.prompt(approved ? "复验意见" : "退回原因", approved ? "复验合格" : "整改不到位");
    if (note === null) return;
    try {
      await flow.verify(hazard.id, approved, note);
      setNotice(approved ? `隐患 #${hazard.id} 已关闭` : `隐患 #${hazard.id} 已退回维保商`);
    } catch (err) {
      setNotice(err instanceof ApiError ? err.message : "复验失败");
    }
  };

  const openLike = (h: HazardTicket) => OPEN_LIKE.includes(h.rectify_status as HStatus);
  const highRisk = (h: HazardTicket) => HIGH_RISK.includes(h.severity as HazardSeverity);
  const openHigh = rows.filter((h) => openLike(h) && highRisk(h));

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">fire-inspect</p>
          <h1>隐患整改</h1>
        </div>
        <span className="muted">未关闭高危 {openHigh.length} 项（设备台账与报表保持封锁）</span>
      </header>

      {notice && <div className="banner info">{notice}</div>}
      {flow.error && <div className="banner danger">{flow.error}</div>}

      <section className="panel">
        <div className="filter-bar">
          {FILTERS.map((f) => (
            <button
              key={f.value || "all"}
              type="button"
              className={filter === f.value ? "chip active" : "chip"}
              onClick={() => setFilter(f.value)}
            >
              {f.label}
            </button>
          ))}
        </div>
      </section>

      <section className="panel wide">
        <div className="table">
          <article className="row head">
            <span>单号</span>
            <span>设备</span>
            <span>等级</span>
            <span>状态</span>
            <span>责任人/期限</span>
            <span>操作（按角色隔离）</span>
          </article>
          {rows.map((hazard) => (
            <article
              className={`row${highRisk(hazard) && openLike(hazard) ? " danger-row" : ""}`}
              key={hazard.id}
            >
              <strong>#{hazard.id}</strong>
              <span>{hazard.device_code ?? `设备#${hazard.device_id}`}</span>
              <HazardSeverityTag value={hazard.severity} />
              <StatusBadge value={hazard.rectify_status} />
              <span className="muted">
                用户 {hazard.owner_id || "未指派"} · {hazard.deadline || "无期限"}
              </span>
              <span className="actions">
                {OPEN_LIKE.includes(hazard.rectify_status as (typeof OPEN_LIKE)[number]) &&
                  can(user?.role, "assignHazard") && (
                    <button type="button" onClick={() => void onAssign(hazard)}>派单</button>
                  )}
                {hazard.rectify_status === HazardRectifyStatus.OPEN &&
                  can(user?.role, "rectifyHazard") && (
                    <button type="button" className="primary" onClick={() => void onRectify(hazard)}>
                      整改完成
                    </button>
                  )}
                {hazard.rectify_status === HazardRectifyStatus.RECTIFIED &&
                  can(user?.role, "verifyHazard") && (
                    <>
                      <button type="button" className="primary" onClick={() => void onVerify(hazard, true)}>
                        复验关闭
                      </button>
                      <button type="button" onClick={() => void onVerify(hazard, false)}>复验退回</button>
                    </>
                  )}
              </span>
            </article>
          ))}
          {rows.length === 0 && <p className="empty">暂无隐患单</p>}
        </div>
      </section>
    </section>
  );
}
