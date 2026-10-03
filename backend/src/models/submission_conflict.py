from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base


class SubmissionConflict(Base):
    """提交冲突区：过期修订/覆盖已复核结果的尝试全部落库，不覆盖现结果。"""

    __tablename__ = "submission_conflict"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, index=True)
    client_submission_id: Mapped[str] = mapped_column(String(128), index=True)
    base_revision: Mapped[int] = mapped_column(Integer)
    current_revision: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(32), index=True)
    payload_preview: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[str] = mapped_column(String(32))
