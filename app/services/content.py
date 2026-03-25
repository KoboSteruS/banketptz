"""
Загрузка и слияние контента страницы с БД.
"""
import json
from typing import Any

from flask import url_for

from app.models import Hall, SiteContent
from app.seed import load_site_defaults_dict


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Рекурсивное слияние словарей (override перекрывает base)."""
    out = dict(base)
    for key, val in override.items():
        if (
            key in out
            and isinstance(out[key], dict)
            and isinstance(val, dict)
        ):
            out[key] = deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def get_merged_site_content() -> dict[str, Any]:
    """Возвращает объединённые дефолты и сохранённый JSON из БД."""
    defaults = load_site_defaults_dict()
    row = SiteContent.query.filter_by(key="main").first()
    if not row:
        return defaults
    try:
        saved = json.loads(row.json_value)
    except json.JSONDecodeError:
        return defaults
    return deep_merge(defaults, saved)


def hall_capacity_list(hall: Hall) -> list[str]:
    try:
        data = json.loads(hall.capacity_lines or "[]")
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def hall_photos_paths(hall: Hall) -> list[str]:
    try:
        data = json.loads(hall.photos_json or "[]")
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def build_venue_photos_urls(halls: list[Hall]) -> dict[str, list[str]]:
    """Словарь slug -> абсолютные URL статики для JS галереи."""
    out: dict[str, list[str]] = {}
    for h in halls:
        paths = hall_photos_paths(h)
        out[h.slug] = [url_for("static", filename=p) for p in paths if p]
    return out


def build_hall_titles_js(halls: list[Hall]) -> dict[str, str]:
    """Подписи для модалки фото: slug -> читаемое название."""
    return {h.slug: h.title_full for h in halls}
