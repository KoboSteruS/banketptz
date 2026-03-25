"""
Подстановка путей к загруженным изображениям после парсинга формы «Тексты».
"""
from typing import Any

from flask import Request
from loguru import logger

from app.utils_upload import allowed_file, save_hall_upload


def _had_file(request: Request, key: str) -> bool:
    f = request.files.get(key)
    return bool(f and f.filename)


def apply_texts_image_uploads(request: Request, parsed: dict[str, Any]) -> list[str]:
    """
    Если для поля прислан файл — сохраняет в static/uploads/site/ и подменяет путь в parsed.
    Возвращает предупреждения (неверный формат файла и т.п.).
    """
    warnings: list[str] = []

    _top_fields: list[tuple[str, str, str, str]] = [
        ("header_logo_file", "header", "logo_path", "Логотип"),
        ("hero_image_file", "hero", "image", "Hero — фон"),
        ("reasons_image_file", "reasons", "image", "Почему мы — фото"),
        ("menu_food_image_file", "menu", "food_image", "Меню — фото блюд"),
        ("menu_corkage_image_file", "menu", "corkage_image", "Меню — пробковый сбор"),
    ]

    for form_key, sec, attr, human in _top_fields:
        if not _had_file(request, form_key):
            continue
        f = request.files[form_key]
        if not allowed_file(f.filename or ""):
            warnings.append(f"{human}: допустимы PNG, JPG, JPEG, WebP, GIF.")
            logger.warning("Отклонена загрузка «{}»: {}", human, f.filename)
            continue
        path = save_hall_upload(f, "site")
        if path:
            parsed[sec][attr] = path

    slides = parsed.get("services", {}).get("slides") or []
    for i in range(len(slides)):
        key = f"slide_{i}_img_file"
        if not _had_file(request, key):
            continue
        f = request.files[key]
        if not allowed_file(f.filename or ""):
            warnings.append(f"Слайд {i + 1} — фото: допустимы PNG, JPG, JPEG, WebP, GIF.")
            continue
        path = save_hall_upload(f, "site")
        if path:
            slides[i]["img"] = path

    return warnings
