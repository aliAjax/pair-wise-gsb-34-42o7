from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base
from src.constants.user_role import UserRole


class UserAccount(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(64), default="")
    role: Mapped[str] = mapped_column(String(32), default=UserRole.INSPECTOR)
    password_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
