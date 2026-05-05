import os
import bcrypt
from fastapi import Request

ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_HASH = os.getenv("ADMIN_PASSWORD_HASH")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify(password: str) -> bool:
    if not ADMIN_HASH:
        return False

    return bcrypt.checkpw(
        password.encode("utf-8"),
        ADMIN_HASH.encode("utf-8")
    )


def is_logged(request: Request) -> bool:
    return request.session.get("user") == ADMIN_USER


def login_user(request: Request, username: str) -> None:
    request.session["user"] = username


def logout_user(request: Request) -> None:
    request.session.clear()

