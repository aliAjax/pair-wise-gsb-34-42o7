"""消防设备服务：台账状态由未关闭隐患实时重算（高危隐患一票否决）。"""

from sqlalchemy.orm import Session

from src.constructors.chain_dto_builder import build_device_dto
from src.constructors.persistence_mapper import orm_to_hazard
from src.models.fire_device import FireDevice


class FireDeviceAppService:
    def __init__(self, db: Session):
        self.db = db

    def list_devices(self, building_id: int | None = None, floor: str | None = None):
        query = self.db.query(FireDevice)
        if building_id is not None:
            query = query.filter(FireDevice.building_id == building_id)
        if floor is not None:
            query = query.filter(FireDevice.floor == floor)
        device_rows = query.order_by(FireDevice.id.asc()).all()
        hazards = [orm_to_hazard(r) for r in self._all_open_hazards()]
        return [build_device_dto(row, hazards) for row in device_rows]

    def _all_open_hazards(self):
        from src.models.hazard_ticket import HazardTicket

        return (
            self.db.query(HazardTicket)
            .filter(HazardTicket.rectify_status.in_(("OPEN", "RECTIFIED")))
            .all()
        )

    def device_history(self, device_id: int):
        from src.constructors.chain_dto_builder import build_hazard_dto, build_result_dto
        from src.models.hazard_ticket import HazardTicket
        from src.models.inspection_result import InspectionResult

        results = (
            self.db.query(InspectionResult)
            .filter(InspectionResult.device_id == device_id)
            .order_by(InspectionResult.id.desc())
            .all()
        )
        hazards = (
            self.db.query(HazardTicket)
            .filter(HazardTicket.device_id == device_id)
            .order_by(HazardTicket.id.desc())
            .all()
        )
        return {
            "results": [build_result_dto(r) for r in results],
            "hazards": [build_hazard_dto(h) for h in hazards],
        }
