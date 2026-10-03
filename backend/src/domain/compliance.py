"""设备合规状态重算：台账与报表共用同一口径，高危隐患一票否决。"""

from __future__ import annotations

from src.constants.device_compliance import DeviceBaseStatus, DeviceCompliance
from src.constants.hazard_severity import HazardSeverity
from src.domain.records import DeviceRecord, HazardRecord


def recompute_device_compliance(device: DeviceRecord, hazards) -> str:
    """返回台账/报表展示状态。存在未关闭 HIGH/CRITICAL 隐患时不得显示正常。"""

    if device.status == DeviceBaseStatus.RETIRED:
        return DeviceCompliance.RETIRED
    if device.status == DeviceBaseStatus.MAINTENANCE:
        return DeviceCompliance.MAINTENANCE

    open_hazards = [
        h for h in hazards if h.device_id == device.id and h.rectify_status in ("OPEN", "RECTIFIED")
    ]
    if any(h.severity in HazardSeverity.HIGH_RISK for h in open_hazards):
        return DeviceCompliance.HIGH_HAZARD_BLOCKED
    if open_hazards:
        return DeviceCompliance.HAZARD_PENDING
    return DeviceCompliance.ACTIVE


def is_compliance_normal(compliance_status: str) -> bool:
    return compliance_status in DeviceCompliance.NORMAL_DISPLAY_ALLOWED


def building_compliance_rate(devices, hazards) -> dict:
    """合规报表口径：被高危隐患封锁的设备不计为正常。"""

    total = len(devices)
    blocked = 0
    open_high = 0
    for device in devices:
        compliance = recompute_device_compliance(device, hazards)
        if compliance == DeviceCompliance.HIGH_HAZARD_BLOCKED:
            blocked += 1
        device_open_high = [
            h
            for h in hazards
            if h.device_id == device.id
            and h.rectify_status in ("OPEN", "RECTIFIED")
            and h.severity in HazardSeverity.HIGH_RISK
        ]
        open_high += len(device_open_high)
    normal = sum(
        1 for d in devices if is_compliance_normal(recompute_device_compliance(d, hazards))
    )
    return {
        "device_total": total,
        "device_normal": normal,
        "device_blocked": blocked,
        "open_high_risk_hazards": open_high,
        "normal_rate": round(normal / total, 4) if total else 0.0,
    }
