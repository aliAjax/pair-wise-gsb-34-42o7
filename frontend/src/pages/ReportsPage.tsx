import { useEffect, useState } from "react";
import { getMonthlyReport } from "../api/Compliance";
import { ApiError } from "../api/client";
import { StatCard } from "../components/common/StatCard";
import { StatusBadge } from "../components/common/StatusBadge";

interface BuildingRate {
  building_id: number;
  building_name: string;
  device_total: number;
  device_normal: number;
  device_blocked: number;
  open_high_risk_hazards: number;
  normal_rate: number;
  task_total: number;
  task_reviewed: number;
}

interface MonthlyReport {
  month: string;
  hazard_total: number;
  hazard_closed: number;
  rectify_rate: number;
  buildings: BuildingRate[];
}

export function ReportsPage() {
  const [report, setReport] = useState<MonthlyReport | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    void getMonthlyReport()
      .then((data) => setReport(data as unknown as MonthlyReport))
      .catch((err) => setError(err instanceof ApiError ? err.message : "加载失败"));
  }, []);

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">fire-inspect</p>
          <h1>合规报表（{report?.month ?? "2026-10"}）</h1>
        </div>
      </header>

      {error && <div className="banner danger">{error}</div>}

      <section className="metrics">
        <StatCard label="隐患总数" value={report?.hazard_total ?? "-"} />
        <StatCard label="已关闭隐患" value={report?.hazard_closed ?? "-"} />
        <StatCard
          label="整改率"
          value={report ? `${Math.round(Number(report.rectify_rate) * 100)}%` : "-"}
        />
      </section>

      <section className="panel wide">
        <h2>按楼栋合规率（高危隐患封锁设备不计正常）</h2>
        <div className="table">
          <article className="row head">
            <span>楼栋</span>
            <span>设备正常/总数</span>
            <span>封锁数</span>
            <span>未关闭高危隐患</span>
            <span>巡检复核</span>
            <span>合规状态</span>
          </article>
          {(report?.buildings ?? []).map((b) => (
            <article className="row" key={b.building_id}>
              <strong>{b.building_name}</strong>
              <span>{b.device_normal}/{b.device_total}（{Math.round(b.normal_rate * 100)}%）</span>
              <span>{b.device_blocked}</span>
              <span>{b.open_high_risk_hazards}</span>
              <span>{b.task_reviewed}/{b.task_total}</span>
              <StatusBadge value={b.device_blocked > 0 ? "HIGH_HAZARD_BLOCKED" : "ACTIVE"} />
            </article>
          ))}
          {!report?.buildings?.length && <p className="empty">暂无报表数据</p>}
        </div>
      </section>
    </section>
  );
}
