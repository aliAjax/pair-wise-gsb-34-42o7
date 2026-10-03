from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base


class AuditLog(Base):
    """审计记录：所有写动作落库；任务重开后仍可追到结果/隐患/审计。"""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int] = mapped_column(Integer, index=True)
    actor_role: Mapped[str] = mapped_column(String(32), index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    target_type: Mapped[str] = mapped_column(String(32))
    target_id: Mapped[str] = mapped_column(String(64), index=True)
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[str] = mapped_column(String(32), index=True)
