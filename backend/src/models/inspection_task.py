from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base
from src.config.settings import settings
from src.constants.inspection_status import InspectionStatus

if settings.sqlalchemy_url.startswith("postgresql"):
    from sqlalchemy.dialects.postgresql import JSONB as _JSON  # type: ignore
else:
    _JSON = JSON


class InspectionTask(Base):
    __tablename__ = "inspection_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    building_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    inspector_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    plan_date: Mapped[str] = mapped_column(String(32), nullable=False)
    task_type: Mapped[str] = mapped_column(String(32), default="ROUTINE")
    status: Mapped[str] = mapped_column(String(32), default=InspectionStatus.PLANNED)
    checklist_version: Mapped[str] = mapped_column(String(32), default="v1")
    finished_at: Mapped[str] = mapped_column(String(32), nullable=True)
    # 乐观锁修订号：检查项修改/复核退回都会自增
    revision: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # 完整检查单（断网恢复后从完整任务继续提交所需）
    checklist_items: Mapped[list] = mapped_column(_JSON, default=list)
    note: Mapped[str] = mapped_column(Text, default="")
