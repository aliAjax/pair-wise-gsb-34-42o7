"""合规报表服务：存在未关闭高危隐患的设备一律不计为正常。"""

from sqlalchemy.orm import Session

from src.constructors.persistence_mapper import orm_to_device, orm_to_hazard
from src.domain.compliance import building_compliance_rate, recompute_device_compliance
from src.models.building import Building
from src.models.fire_device import FireDevice
from src.models.hazard_ticket import HazardTicket
from src.models.inspection_task import InspectionTask


class ComplianceAppService:
    def __init__(self, db: Session):
        self.db = db

    def dashboard(self):
        devices = [orm_to_device(r) for r in self.db.query(FireDevice).all()]
        hazards = [orm_to_hazard(r) for r in self.db.query(HazardTicket).all()]
        open_hazards = [h for h in hazards if h.rectify_status in ("OPEN", "RECTIFIED")]
        high_open = [h for h in open_hazards if h.severity in ("HIGH", "CRITICAL")]
        blocked_devices = {
            d.id for d in devices
            if recompute_device_compliance(d, hazards) == "HIGH_HAZARD_BLOCKED"
        }
        tasks = self.db.query(InspectionTask).all()
        total_tasks = len(tasks)
        reviewed = sum(1 for t in tasks if t.status == "REVIEWED")
        return {
            "device_total": len(devices),
            "open_hazard_total": len(open_hazards),
            "open_high_risk_hazards": len(high_open),
            "high_risk_blocked_devices": len(blocked_devices),
            "blocked_device_ids": sorted(blocked_devices),
            "task_total": total_tasks,
            "task_reviewed": reviewed,
            "inspection_completion_rate": round(reviewed / total_tasks, 4) if total_tasks else 0.0,
        }

    def monthly_report(self):
        devices = [orm_to_device(r) for r in self.db.query(FireDevice).all()]
        hazards = [orm_to_hazard(r) for r in self.db.query(HazardTicket).all()]
        tasks = self.db.query(InspectionTask).all()
        buildings = self.db.query(Building).all()

        per_building = []
        for building in buildings:
            b_devices = [d for d in devices if d.building_id == building.id]
            rate = building_compliance_rate(b_devices, hazards)
            b_tasks = [t for t in tasks if t.building_id == building.id]
            rate["building_id"] = building.id
            rate["building_name"] = building.name
            rate["task_total"] = len(b_tasks)
            rate["task_reviewed"] = sum(1 for t in b_tasks if t.status == "REVIEWED")
            per_building.append(rate)

        total_hazards = len(hazards)
        closed = sum(1 for h in hazards if h.rectify_status == "CLOSED")
        return {
            "month": "2026-10",
            "buildings": per_building,
            "hazard_total": total_hazards,
            "hazard_closed": closed,
            "rectify_rate": round(closed / total_hazards, 4) if total_hazards else 0.0,
        }
