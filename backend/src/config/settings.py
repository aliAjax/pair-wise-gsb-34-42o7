"""全局配置：值来自环境变量；新增配置必须同步 .env.example / docker-compose.yml。"""

import os


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    PORT = int(os.getenv("PORT", "8000"))
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "app_db")
    DB_USER = os.getenv("DB_USER", "app_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "app_password")
    # 测试/本地无 PG 时可 sqlite:///./fire_inspect.db
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
    JWT_SECRET = os.getenv("JWT_SECRET", "local-dev-secret")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
    SEED_ON_START = _bool(os.getenv("SEED_ON_START", "true"))
    API_PREFIX = "/api"

    @property
    def sqlalchemy_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
