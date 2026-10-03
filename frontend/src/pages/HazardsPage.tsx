import { useEffect, useState } from "react";
import { useHazardFlow } from "../hooks/useHazardFlow";
import { HazardSeverityTag } from "../components/common/HazardSeverityTag";
import { StatusBadge } from "../components/common/StatusBadge";
import { RectifyStatusText } from "../constants/RectifyStatus";
import { currentRole } from "../api/client";
import { can } from "../constants/roles";

export function HazardsPage() {
  const { hazards, close, isOpen } = useHazardFlow();
  const [message, setMessage] = useState("");
  const role = currentRole();
  useEffect(() => {
    hazards.load();
  }, []);
  const onClose = async (ticketId: number) => {
    setMessage("");
    try {
      await close(ticketId, "现场整改完成");
      setMessage("隐患单已关闭，设备台账状态已重算");
    } catch (err) {
      setMessage((err as Error).message);
    }
  };
  return <section>
    <h2>隐患整改</h2>
    <div className="panel wide">
      <div className="table">
        {hazards.rows.map((ticket) => <article key={ticket.id} className="row">
          <strong>#{ticket.id} · {ticket.item_code}</strong>
          <HazardSeverityTag value={ticket.severity} />
          <span>设备 {ticket.device_id} · 提交 {ticket.submission_id || "-"}</span>
          <StatusBadge value={ticket.rectify_status} />
          <span>{RectifyStatusText[ticket.rectify_status as keyof typeof RectifyStatusText] ?? ticket.rectify_status}</span>
          {isOpen(ticket) && can(role, "hazard:close") && (
            <button onClick={() => onClose(ticket.id)}>整改关闭</button>
          )}
        </article>)}
      </div>
      {message && <p className="message">{message}</p>}
    </div>
  </section>;
}
