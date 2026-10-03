"""数据库种子：全部本地数据，无第三方 API。"""

from __future__ import annotations

from sqlalchemy import select

from src.config.database import SessionLocal, init_schema
from src.constants.device_compliance import DeviceBaseStatus
from src.constants.device_type import DeviceType
from src.constants.hazard_severity import HazardSeverity
from src.constants.inspection_status import InspectionStatus
from src.constants.user_role import UserRole
from src.models.building import Building
from src.models.fire_device import FireDevice
from src.models.inspection_result import InspectionResult
from src.models.inspection_task import InspectionTask
from src.models.user_account import UserAccount
from src.utils.security import hash_password

SEED_USERS = [
    ("inspector", "巡检员-王磊", UserRole.INSPECTOR, "inspect123"),
    ("maintainer", "维保商-安泰消防", UserRole.MAINTAINER, "maintain123"),
    ("supervisor", "物业主管-周敏", UserRole.SUPERVISOR, "super123"),
    ("auditor", "审计员-陈立", UserRole.AUDITOR, "audit123"),
]


def seed_database() -> None:
    init_schema()
    db = SessionLocal()
    try:
        if db.scalars(select(UserAccount)).first():
            return

        for username, display_name, role, password in SEED_USERS:
            db.add(
                UserAccount(
                    username=username,
                    display_name=display_name,
                    role=role,
                    password_sha256=hash_password(password),
                )
            )

        building = Building(
            name="A 座研发楼",
            campus="江北科技园",
            floor_count=12,
            fire_grade="GRADE_1",
            manager_id=3,
            address_code="320100-A01",
        )
        db.add(building)
        db.flush()

        devices = [
            FireDevice(
                building_id=building.id,
                device_code="FE-HYDRANT-001",
                device_type=DeviceType.HYDRANT,
                floor="1",
                location_desc="大堂东侧消火栓",
                install_date="2024-05-01",
                status=DeviceBaseStatus.NORMAL,
                next_maintenance_at="2026-11-01",
                owner_id=2,
            ),
            FireDevice(
                building_id=building.id,
                device_code="FE-SMOKE-001",
                device_type=DeviceType.SMOKE_DETECTOR,
                floor="3",
                location_desc="3F 走廊烟感",
                install_date="2024-05-01",
                status=DeviceBaseStatus.NORMAL,
                next_maintenance_at="2026-11-01",
                owner_id=2,
            ),
            FireDevice(
                building_id=building.id,
                device_code="FE-EXIT-001",
                device_type=DeviceType.EXIT_LIGHT,
                floor="3",
                location_desc="3F 疏散指示灯",
                install_date="2024-05-01",
                status=DeviceBaseStatus.NORMAL,
                next_maintenance_at="2026-12-01",
                owner_id=2,
            ),
        ]
        db.add_all(devices)
        db.flush()

        task = InspectionTask(
            building_id=building.id,
            inspector_id=1,
            plan_date="2026-10-03",
            task_type="ROUTINE",
            status=InspectionStatus.PLANNED,
            checklist_version="v1",
            revision=1,
            checklist_items=[
                {
                    "item_code": "CHK-PRESSURE-1F",
                    "device_id": devices[0].id,
                    "title": "消火栓静水压力",
                    "default_severity": HazardSeverity.HIGH,
                    "active": True,
                },
                {
                    "item_code": "CHK-SMOKE-3F",
                    "device_id": devices[1].id,
                    "title": "烟感探头响应",
                    "default_severity": HazardSeverity.CRITICAL,
                    "active": True,
                },
                {
                    "item_code": "CHK-EXIT-3F",
                    "device_id": devices[2].id,
                    "title": "疏散指示标识",
                    "default_severity": HazardSeverity.MEDIUM,
                    "active": True,
                },
            ],
        )
        db.add(task)
        db.flush()
        for item in task.checklist_items:
            db.add(
                InspectionResult(
                    task_id=task.id,
                    device_id=item["device_id"],
                    item_code=item["item_code"],
                    result_status="PENDING",
                    review_state="DRAFT",
                    severity_hint=item["default_severity"],
                    revision=1,
                )
            )
        db.commit()
    finally:
        db.close()
