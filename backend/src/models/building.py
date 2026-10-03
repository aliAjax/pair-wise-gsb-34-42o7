from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base


class Building(Base):
    __tablename__ = "building"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    campus: Mapped[str] = mapped_column(String(128), default="")
    floor_count: Mapped[int] = mapped_column(Integer, default=1)
    fire_grade: Mapped[str] = mapped_column(String(32), default="GRADE_2")
    manager_id: Mapped[int] = mapped_column(Integer, nullable=True)
    address_code: Mapped[str] = mapped_column(String(64), default="")
