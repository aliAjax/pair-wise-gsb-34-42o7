from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base
from src.constants.device_compliance import DeviceBaseStatus


class FireDevice(Base):
    __tablename__ = "fire_device"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    building_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    device_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    device_type: Mapped[str] = mapped_column(String(32), nullable=False)
    floor: Mapped[str] = mapped_column(String(16), default="1")
    location_desc: Mapped[str] = mapped_column(String(255), default="")
    install_date: Mapped[str] = mapped_column(String(32), default="")
    # 主数据状态；台账/合规展示状态由未关闭隐患实时重算，禁止直接写“正常”覆盖
    status: Mapped[str] = mapped_column(String(32), default=DeviceBaseStatus.NORMAL)
    next_maintenance_at: Mapped[str] = mapped_column(String(32), nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, nullable=True)
