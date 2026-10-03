"""认证 controller：登录。"""

from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.services.auth_service import AuthService
from src.types.chain_payloads import LoginPayload


def login_controller(payload: LoginPayload, db: Session = Depends(get_db)):
    return AuthService(db).login(payload.username, payload.password)
