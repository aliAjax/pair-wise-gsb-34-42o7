import { useEffect, useState } from "react";
import { getDashboard } from "../api/Compliance";
import { listHazards } from "../api/HazardTicket";
import { ApiError } from "../api/client";
import { StatCard } from "../components/common/StatCard";
import { StatusBadge } from "../components/common/StatusBadge";
import { HazardSeverityTag } from "../components/common/HazardSeverityTag";
import { HazardRectifyStatusText } from "../constants/HazardRectifyStatus";
import type { DashboardSummary } from "../types/Chain";
import type { HazardTicket } from "../types/HazardTicket";

export function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [highHazards, setHighHazards] = useState<HazardTicket[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    void (async () => {
      try {
        const [dash, hazards] = await Promise.all([
          getDashboard(),
          listHazards(),
        ]);
        setSummary(dash);
        setHighHazards(
          hazards.filter(
            (h) =>
              ["HIGH", "CRITICAL"].includes(h.severity) &&
              ["OPEN", "RECTIFIED"].includes(h.rectify_status),
          ),
        );
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "加载失败");
      }
    })();
  }, []);

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">fire-inspect</p>
          <h1>消防合规总览</h1>
        </div>
        <StatusBadge value={summary && summary.open_high_risk_hazards > 0 ? "HIGH_HAZARD_BLOCKED" : "ACTIVE"} />
      </header>

      {error && <div className="banner danger">{error}</div>}

      <section className="metrics">
        <StatCard label="设备总数" value={summary?.device_total ?? "-"} />
        <StatCard
          label="未关闭高危隐患"
          value={summary?.open_high_risk_hazards ?? "-"}
        />
        <StatCard
          label="被高危封锁设备"
          value={summary?.high_risk_blocked_devices ?? "-"}
        />
        <StatCard label="未关闭隐患" value={summary?.open_hazard_total ?? "-"} />
        <StatCard
          label="巡检复核完成率"
          value={summary ? `${Math.round(summary.inspection_completion_rate * 100)}%` : "-"}
        />
      </section>

      <section className="panel wide">
        <h2>高危隐患未关闭清单（台账/报表不得显示正常）</h2>
        {highHazards.length === 0 ? (
          <p className="empty">暂无未关闭的高危/特高隐患</p>
        ) : (
          <div className="table">
            {highHazards.map((hazard) => (
              <article className="row" key={hazard.id}>
                <strong>#{hazard.id} 设备 {hazard.device_id}</strong>
                <HazardSeverityTag value={hazard.severity} />
                <StatusBadge value={hazard.rectify_status} />
                <span className="muted">
                  {HazardRectifyStatusText[hazard.rectify_status as keyof typeof HazardRectifyStatusText]} ·
                  期限 {hazard.deadline || "-"}
                </span>
              </article>
            ))}
          </div>
        )}
        {summary && summary.high_risk_blocked_devices.length > 0 && (
          <div className="banner danger">
            被封锁设备 ID：{summary.blocked_device_ids.join("、")}
          </div>
        )}
      </section>
    </section>
  );
}
