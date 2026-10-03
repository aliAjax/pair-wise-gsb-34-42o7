from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.constants.hazard_severity import HIGH_RISK_SEVERITIES
from src.constants.rectify_status import OPEN_RECTIFY_STATUSES
from src.constants.log_templates import LOG_TEMPLATES

class FireDeviceService:
    """设备台账状态由未关闭隐患实时推导：存在未关闭高危隐患时不得显示正常。"""
    def __init__(self):
        self.repo = FireDeviceRepository()
        self.hazard_repo = HazardTicketRepository()
    def _open_hazards(self, device_id):
        return [t for t in self.hazard_repo.find_all()
                if t["device_id"] == device_id and t["rectify_status"] in OPEN_RECTIFY_STATUSES]
    def derive_status(self, device_id):
        open_hazards = self._open_hazards(device_id)
        if any(t["severity"] in HIGH_RISK_SEVERITIES for t in open_hazards):
            return "ABNORMAL"
        if open_hazards:
            return "MAINTENANCE"
        return "NORMAL"
    def _enrich(self, row):
        open_hazards = self._open_hazards(row["id"])
        derived = self.derive_status(row["id"])
        return {
            **row,
            "status": derived,
            "open_hazard_count": len(open_hazards),
            "open_high_hazard_count": len([t for t in open_hazards if t["severity"] in HIGH_RISK_SEVERITIES])
        }
    def list(self):
        return [self._enrich(row) for row in self.repo.find_all()]
    def get(self, device_id):
        row = self.repo.find_by_id(device_id)
        return self._enrich(row) if row else None
    def recompute(self, device_id, audit=None, actor=None):
        """隐患或检查项变化后重算台账状态并留痕。"""
        row = self.repo.find_by_id(device_id)
        if not row:
            return None
        derived = self.derive_status(device_id)
        if row["status"] != derived:
            row["status"] = derived
            self.repo.save(row)
            if audit:
                audit.record(LOG_TEMPLATES["FireDevice"][4], actor or {}, "FireDevice", device_id,
                             f"status -> {derived}")
        return self._enrich(row)
