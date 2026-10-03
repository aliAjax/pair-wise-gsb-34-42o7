from sqlalchemy import Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base
from src.constants.result_status import ResultStatus
from src.constants.review_state import ReviewState

# 在途（非 DISCARDED）结果同一任务同一检查项唯一
_active_result_where = text("review_state != 'DISCARDED'")


class InspectionResult(Base):
    __tablename__ = "inspection_result"
    __table_args__ = (
        Index(
            "uq_result_active_item",
            "task_id",
            "item_code",
            unique=True,
            sqlite_where=_active_result_where,
            postgresql_where=_active_result_where,
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    device_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    item_code: Mapped[str] = mapped_column(String(64), nullable=False)
    result_status: Mapped[str] = mapped_column(String(16), default=ResultStatus.PENDING)
    measured_value: Mapped[str] = mapped_column(String(255), default="")
    photo_url: Mapped[str] = mapped_column(String(255), default="")
    note: Mapped[str] = mapped_column(Text, default="")
    review_state: Mapped[str] = mapped_column(String(16), default=ReviewState.DRAFT)
    severity_hint: Mapped[str] = mapped_column(String(16), default="MEDIUM")
    revision: Mapped[int] = mapped_column(Integer, default=1)
    submitted_at: Mapped[str] = mapped_column(String(32), nullable=True)
    reviewed_at: Mapped[str] = mapped_column(String(32), nullable=True)
    returned_at: Mapped[str] = mapped_column(String(32), nullable=True)
