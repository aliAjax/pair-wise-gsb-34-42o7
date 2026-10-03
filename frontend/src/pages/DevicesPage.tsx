import { useEffect } from "react";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { StatusBadge } from "../components/common/StatusBadge";
import { DeviceLocationCell } from "../components/common/DeviceLocationCell";
import { DeviceStatusText } from "../constants/DeviceStatus";
import { ERROR_MESSAGES } from "../constants/errorMessages";

export function DevicesPage() {
  const store = useFireDeviceStore();
  useEffect(() => {
    store.load();
  }, []);
  const abnormal = store.rows.filter((row) => row.status === "ABNORMAL");
  return <section>
    <h2>消防设备台账</h2>
    {abnormal.length > 0 && (
      <div className="panel alert">
        {ERROR_MESSAGES.HAZARD_STILL_OPEN}：{abnormal.map((row) => row.device_code).join("、")}
      </div>
    )}
    <div className="panel wide">
      <div className="table">
        {store.rows.map((device) => <article key={device.id} className="row">
          <strong>{device.device_code}</strong>
          <span>{device.device_type}</span>
          <DeviceLocationCell device={device} />
          <span>未关闭隐患 {device.open_hazard_count ?? 0}（高危 {device.open_high_hazard_count ?? 0}）</span>
          <StatusBadge value={device.status} />
          <span>{DeviceStatusText[device.status as keyof typeof DeviceStatusText] ?? device.status}</span>
        </article>)}
      </div>
    </div>
  </section>;
}
