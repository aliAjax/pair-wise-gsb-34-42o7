from sqlalchemy import Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base
from src.constants.hazard_severity import HazardRectifyStatus, HazardSeverity

_open_hazard_where = text("active_key = 'ACTIVE'")


class HazardTicket(Base):
    __tablename__ = "hazard_ticket"
    __table_args__ = (
        # 一条检查结果至多一张在途隐患单（同一提交重试不重复生成）
        Index(
            "uq_hazard_open_per_result",
            "result_id",
            unique=True,
            sqlite_where=_open_hazard_where,
            postgresql_where=_open_hazard_where,
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    result_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    device_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default=HazardSeverity.MEDIUM)
    owner_id: Mapped[int] = mapped_column(Integer, default=0)
    deadline: Mapped[str] = mapped_column(String(32), default="")
    rectify_status: Mapped[str] = mapped_column(String(16), default=HazardRectifyStatus.OPEN)
    rectify_note: Mapped[str] = mapped_column(Text, default="")
    closed_at: Mapped[str] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=True)
    # OPEN/RECTIFIED 时为 'ACTIVE'，关闭/撤销后为 NULL（配合部分唯一索引）
    active_key: Mapped[str] = mapped_column(String(16), nullable=True)
