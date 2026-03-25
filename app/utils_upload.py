"""
Сохранение загруженных файлов в static/uploads.
"""
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = frozenset({"png", "jpg", "jpeg", "webp", "gif"})


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_hall_upload(file: FileStorage, subfolder: str = "halls") -> str | None:
    """
    Сохраняет файл в static/uploads/<subfolder>/, возвращает путь для static (uploads/...).
    """
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        return None
    ext = secure_filename(file.filename.rsplit(".", 1)[1].lower())
    name = f"{uuid.uuid4().hex}.{ext}"
    static_root = Path(current_app.root_path) / "static"
    dest_dir = static_root / "uploads" / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / name
    file.save(str(path))
    return f"uploads/{subfolder}/{name}"
