"""SQLAlchemy 2.0 引擎与会话。SQLite 需打开外键约束（测试用）。"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config.settings import settings


class Base(DeclarativeBase):
    pass


connect_args = {"check_same_thread": False} if settings.sqlalchemy_url.startswith("sqlite") else {}
engine = create_engine(settings.sqlalchemy_url, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

if settings.sqlalchemy_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_schema():
    # 触发模型注册
    from src.models import building as _building  # noqa: F401
    from src.models import fire_device as _fire_device  # noqa: F401
    from src.models import inspection_task as _inspection_task  # noqa: F401
    from src.models import inspection_result as _inspection_result  # noqa: F401
    from src.models import hazard_ticket as _hazard_ticket  # noqa: F401
    from src.models import user_account as _user_account  # noqa: F401
    from src.models import audit_log as _audit_log  # noqa: F401
    from src.models import submission_conflict as _submission_conflict  # noqa: F401
    from src.models import submission_record as _submission_record  # noqa: F401

    Base.metadata.create_all(bind=engine)
