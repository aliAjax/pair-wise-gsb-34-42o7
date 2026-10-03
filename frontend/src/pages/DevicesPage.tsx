import { useEffect, useMemo, useState } from "react";
import { listFireDevices } from "../api/FireDevice";
import { ApiError } from "../api/client";
import { StatusBadge } from "../components/common/StatusBadge";
import { DeviceComplianceText } from "../constants/DeviceCompliance";
import { DeviceTypeText } from "../constants/DeviceType";
import type { FireDevice } from "../types/FireDevice";

export function DevicesPage() {
  const [rows, setRows] = useState<FireDevice[]>([]);
  const [floor, setFloor] = useState("");
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setRows(await listFireDevices(floor ? { floor } : undefined));
      setError("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "加载失败");
    }
  };

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [floor]);

  const floors = useMemo(
    () => Array.from(new Set(rows.map((r) => r.floor))).sort(),
    [rows],
  );

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">fire-inspect</p>
          <h1>消防设备台账</h1>
        </div>
      </header>

      {error && <div className="banner danger">{error}</div>}

      <section className="panel">
        <div className="filter-bar">
          <label>
            楼层筛选
            <select value={floor} onChange={(e) => setFloor(e.target.value)}>
              <option value="">全部楼层</option>
              {floors.map((f) => (
                <option key={f} value={f}>{f} 层</option>
              ))}
            </select>
          </label>
        </div>
      </section>

      <section className="panel wide">
        <h2>设备列表（状态由未关闭隐患实时重算）</h2>
        <div className="table">
          <article className="row head">
            <span>设备编号</span>
            <span>类型</span>
            <span>楼层/位置</span>
            <span>合规状态</span>
            <span>下次维保</span>
          </article>
          {rows.map((device) => (
            <article className="row" key={device.id}>
              <strong>{device.device_code}</strong>
              <span>{DeviceTypeText[device.device_type as keyof typeof DeviceTypeText] ?? device.device_type}</span>
              <span>{device.floor}F · {device.location_desc}</span>
              <StatusBadge value={device.status} />
              <span className="muted">{device.next_maintenance_at ?? "-"}</span>
            </article>
          ))}
          {rows.length === 0 && <p className="empty">暂无设备</p>}
        </div>
        <p className="muted small">
          状态口径：{Object.values(DeviceComplianceText).join(" / ")}。存在未关闭 HIGH/CRITICAL 隐患时不会出现“正常”。
        </p>
      </section>
    </section>
  );
}
