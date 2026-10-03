"""认证服务：登录签发 JWT。"""

from src.constants.log_templates import AuditAction
from src.domain import errors
from src.models.audit_log import AuditLog
from src.repositories.chain_repository import ChainRepository
from src.utils.jwt_service import create_access_token
from src.utils.security import verify_password
from src.domain.records import utc_now_iso


class AuthService:
    def __init__(self, db):
        self.db = db
        self.repo = ChainRepository(db)

    def login(self, username: str, password: str) -> dict:
        user = self.repo.get_user_by_name(username)
        if user is None or not verify_password(password, user.password_sha256):
            raise errors.AuthInvalidError("用户名或密码错误")
        token = create_access_token(user.id, user.username, user.role)
        self.db.add(
            AuditLog(
                actor_id=user.id,
                actor_role=user.role,
                action=AuditAction.AUTH_LOGIN,
                target_type="UserAccount",
                target_id=str(user.id),
                detail=f"login username={user.username}",
                created_at=utc_now_iso(),
            )
        )
        self.db.commit()
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "role": user.role,
            },
        }
