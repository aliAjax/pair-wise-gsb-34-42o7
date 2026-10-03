import { useEffect } from "react";
import { useReportStore } from "../stores/ReportStore";
import { StatCard } from "../components/common/StatCard";
import { StatusBadge } from "../components/common/StatusBadge";
import { EmptyState } from "../components/common/EmptyState";
import { formatNumber } from "../utils/formatters";

export function ReportsPage() {
  const store = useReportStore();
  useEffect(() => {
    store.load().catch(() => undefined);
  }, []);
  const report = store.report;
  if (!report) return <section><h2>合规报表</h2><EmptyState title="报表加载中或暂无数据" /></section>;
  return <section>
    <h2>合规报表</h2>
    <div className="metrics">
      <StatCard label="未关闭高危隐患" value={formatNumber(report.summary.open_high_hazards)} />
      <StatCard label="异常设备" value={formatNumber(report.summary.device_abnormal)} />
      <StatCard label="全局合规状态" value={report.summary.compliance_status} />
    </div>
    <div className="panel wide">
      <h2>楼栋合规（存在未关闭高危隐患不得显示正常）</h2>
      <div className="table">
        {report.buildings.map((row) => <article key={row.building_id} className="row">
          <strong>{row.building_name}</strong>
          <span>复核率 {(row.review_rate * 100).toFixed(0)}%</span>
          <span>整改率 {(row.rectify_rate * 100).toFixed(0)}%</span>
          <span>故障率 {(row.device_fault_rate * 100).toFixed(0)}%</span>
          <span>高危未关 {row.open_high_hazards}</span>
          <StatusBadge value={row.compliance_status} />
        </article>)}
      </div>
    </div>
    <div className="panel wide">
      <h2>设备合规明细</h2>
      <div className="table">
        {report.devices.map((device) => <article key={device.id} className="row">
          <strong>{device.device_code}</strong>
          <span>高危未关 {device.open_high_hazard_count ?? 0}</span>
          <StatusBadge value={device.status} />
        </article>)}
      </div>
    </div>
  </section>;
}
