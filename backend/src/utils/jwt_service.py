"""JWT 签发与校验（python-jose）。"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from src.config.settings import settings
from src.constants.user_role import UserRole


def create_access_token(user_id: int, username: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise ValueError(str(exc)) from exc


def is_valid_role(role: str) -> bool:
    return role in UserRole.ALL
