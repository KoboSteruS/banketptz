"""
Проверка доступа к админке по сегменту URL (секрет или JWT).
"""
import secrets

import jwt
from flask import abort, current_app


def verify_admin_token(token: str | None) -> bool:
    """
    Допуск: совпадение с ADMIN_SECRET_TOKEN (constant-time)
    или валидный JWT HS256 с admin: true или role == 'admin'.
    """
    if not token:
        return False

    plain = current_app.config.get("ADMIN_SECRET_TOKEN") or ""
    if plain and secrets.compare_digest(token, plain):
        return True

    jwt_secret = current_app.config.get("JWT_SECRET_KEY") or current_app.config.get(
        "SECRET_KEY"
    )
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return False

    if payload.get("admin") is True:
        return True
    if payload.get("role") == "admin":
        return True
    return False


def require_admin_token(token: str | None) -> None:
    """404 если токен невалиден (не раскрывать наличие админки)."""
    if not verify_admin_token(token):
        abort(404)
