from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base
from src.config.settings import settings

if settings.sqlalchemy_url.startswith("postgresql"):
    from sqlalchemy.dialects.postgresql import JSONB as _JSON  # type: ignore
else:
    from sqlalchemy import JSON as _JSON


class SubmissionRecord(Base):
    """提交幂等记录：同一 client_submission_id 重试只回放首次结果。"""

    __tablename__ = "submission_record"
    __table_args__ = (
        UniqueConstraint("task_id", "client_submission_id", name="uq_submission_idempotency"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, index=True)
    client_submission_id: Mapped[str] = mapped_column(String(128))
    inspector_id: Mapped[int] = mapped_column(Integer)
    base_revision: Mapped[int] = mapped_column(Integer)
    outcome_json: Mapped[dict] = mapped_column(_JSON, default=dict)
    created_at: Mapped[str] = mapped_column(String(32))
