"""密码哈希：零第三方依赖（stdlib sha256+salt）。"""

import hashlib
import hmac


def hash_password(password: str, salt: str = "fire-inspect") -> str:
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def verify_password(password: str, password_sha256: str, salt: str = "fire-inspect") -> bool:
    return hmac.compare_digest(hash_password(password, salt), password_sha256)
