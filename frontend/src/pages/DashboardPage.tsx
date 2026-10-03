import { useEffect } from "react";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { useHazardTicketStore } from "../stores/HazardTicketStore";
import { useInspectionTaskStore } from "../stores/InspectionTaskStore";
import { StatCard } from "../components/common/StatCard";
import { StatusBadge } from "../components/common/StatusBadge";
import { HazardSeverityTag } from "../components/common/HazardSeverityTag";
import { OPEN_RECTIFY_STATUSES } from "../constants/RectifyStatus";

export function DashboardPage() {
  const devices = useFireDeviceStore();
  const hazards = useHazardTicketStore();
  const tasks = useInspectionTaskStore();
  useEffect(() => {
    devices.load();
    hazards.load();
    tasks.load();
  }, []);
  const openHigh = hazards.rows.filter(
    (row) => OPEN_RECTIFY_STATUSES.includes(row.rectify_status as never) && ["HIGH", "CRITICAL"].includes(row.severity)
  );
  const abnormal = devices.rows.filter((row) => row.status === "ABNORMAL");
  const reviewed = tasks.rows.filter((row) => row.status === "REVIEWED").length;
  return <section>
    <h2>消防合规总览</h2>
    <div className="metrics">
      <StatCard label="设备总数" value={devices.rows.length} />
      <StatCard label="异常设备" value={abnormal.length} />
      <StatCard label="未关闭高危隐患" value={openHigh.length} />
      <StatCard label="已复核任务" value={`${reviewed}/${tasks.rows.length}`} />
    </div>
    <div className="panel wide">
      <h2>高危隐患</h2>
      <div className="table">
        {openHigh.map((ticket) => <article key={ticket.id} className="row">
          <strong>#{ticket.id} · {ticket.item_code}</strong>
          <HazardSeverityTag value={ticket.severity} />
          <StatusBadge value={ticket.rectify_status} />
        </article>)}
        {openHigh.length === 0 && <p>当前没有未关闭的高危隐患。</p>}
      </div>
    </div>
  </section>;
}
