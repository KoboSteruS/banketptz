"""
Роуты главных страниц лендинга.
"""
from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    """Главная страница — одностраничный лендинг банкетных залов."""
    return render_template("index.html")
