"""
Конфигурация приложения Banket.
"""
import os
from pathlib import Path


class Config:
    """Базовые настройки Flask."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me-in-production")
    BASE_DIR = Path(__file__).resolve().parent.parent
    INSTANCE_PATH = BASE_DIR / "instance"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + str(INSTANCE_PATH / "banket.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024

    # Секрет для входа в админке: https://домен/<ADMIN_SECRET_TOKEN>/admin/
    # Либо JWT (HS256) с admin: true или role: "admin"
    ADMIN_SECRET_TOKEN = os.environ.get(
        "ADMIN_SECRET_TOKEN",
        "dev-admin-token-replace-in-production",
    )
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)

    # Уведомления о заявках с формы (VK messages.send)
    VK_ACCESS_TOKEN = os.environ.get("VK_ACCESS_TOKEN", "")
    VK_NOTIFY_USER_IDS = os.environ.get("VK_NOTIFY_USER_IDS", "")
