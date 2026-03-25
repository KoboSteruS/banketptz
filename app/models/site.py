"""
Модели контента сайта и залов.
"""
import uuid

from app.extensions import db


class SiteContent(db.Model):
    """JSON-контент страницы (тексты, пути к картинкам, карта)."""

    __tablename__ = "site_content"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, default="main")
    json_value = db.Column(db.Text, nullable=False)


class Hall(db.Model):
    """Банкетный зал."""

    __tablename__ = "halls"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = db.Column(db.String(64), unique=True, nullable=False, index=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    title_short = db.Column(db.String(255), nullable=False)
    title_full = db.Column(db.String(255), nullable=False)
    meta_line = db.Column(db.String(255), default="")
    capacity_lines = db.Column(db.Text, nullable=False, default="[]")
    address_line = db.Column(db.String(512), default="")
    maps_link = db.Column(db.String(1024), default="")
    image_gallery = db.Column(db.String(512), default="")
    image_detail = db.Column(db.String(512), default="")
    photos_json = db.Column(db.Text, nullable=False, default="[]")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
