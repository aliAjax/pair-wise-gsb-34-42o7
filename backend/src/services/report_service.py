from src.repositories.building_repository import BuildingRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.services.fire_device_service import FireDeviceService
from src.constants.hazard_severity import HIGH_RISK_SEVERITIES
from src.constants.rectify_status import OPEN_RECTIFY_STATUSES

class ReportService:
    """合规报表：存在未关闭高危隐患的楼栋与设备不得显示正常。"""
    def __init__(self):
        self.building_repo = BuildingRepository()
        self.task_repo = InspectionTaskRepository()
        self.hazard_repo = HazardTicketRepository()
        self.device_service = FireDeviceService()
    def compliance(self):
        devices = self.device_service.list()
        hazards = self.hazard_repo.find_all()
        tasks = self.task_repo.find_all()
        open_high = [t for t in hazards if t["rectify_status"] in OPEN_RECTIFY_STATUSES
                     and t["severity"] in HIGH_RISK_SEVERITIES]
        buildings = []
        for building in self.building_repo.find_all():
            b_devices = [d for d in devices if d["building_id"] == building["id"]]
            b_tasks = [t for t in tasks if t["building_id"] == building["id"]]
            b_hazards = [h for h in hazards if h["device_id"] in {d["id"] for d in b_devices}]
            b_open_high = [h for h in b_hazards if h["rectify_status"] in OPEN_RECTIFY_STATUSES
                           and h["severity"] in HIGH_RISK_SEVERITIES]
            reviewed = len([t for t in b_tasks if t["status"] == "REVIEWED"])
            closed = len([h for h in b_hazards if h["rectify_status"] == "CLOSED"])
            abnormal = len([d for d in b_devices if d["status"] == "ABNORMAL"])
            buildings.append({
                "building_id": building["id"],
                "building_name": building["name"],
                "task_total": len(b_tasks),
                "task_reviewed": reviewed,
                "review_rate": round(reviewed / len(b_tasks), 4) if b_tasks else 0,
                "hazard_total": len(b_hazards),
                "hazard_closed": closed,
                "rectify_rate": round(closed / len(b_hazards), 4) if b_hazards else 1,
                "device_total": len(b_devices),
                "device_abnormal": abnormal,
                "device_fault_rate": round(abnormal / len(b_devices), 4) if b_devices else 0,
                "open_high_hazards": len(b_open_high),
                "compliance_status": "ABNORMAL" if b_open_high else "NORMAL"
            })
        return {
            "buildings": buildings,
            "devices": devices,
            "summary": {
                "open_high_hazards": len(open_high),
                "device_abnormal": len([d for d in devices if d["status"] == "ABNORMAL"]),
                "compliance_status": "ABNORMAL" if open_high else "NORMAL"
            }
        }
