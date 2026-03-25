"""
Роуты главных страниц лендинга.
"""
from flask import Blueprint, render_template

from app.models import Hall
from app.services.content import (
    build_hall_titles_js,
    build_venue_photos_urls,
    get_merged_site_content,
)

pages_bp = Blueprint("pages", __name__)


def _services_text_data(content: dict) -> list[dict]:
    slides = content.get("services", {}).get("slides", [])
    out = []
    for s in slides:
        out.append(
            {
                "title": s.get("title", ""),
                "desc": s.get("desc", ""),
                "btn": s.get("btn", ""),
            }
        )
    return out


@pages_bp.route("/")
def index():
    """Главная страница — одностраничный лендинг банкетных залов."""
    content = get_merged_site_content()
    halls = Hall.query.filter_by(is_active=True).order_by(Hall.sort_order).all()
    venue_photos = build_venue_photos_urls(halls)
    hall_titles_js = build_hall_titles_js(halls)
    slides = content.get("services", {}).get("slides", [])
    n_slides = len(slides) if slides else 1
    slide_pct = 100.0 / n_slides
    return render_template(
        "index.html",
        content=content,
        halls=halls,
        venue_photos=venue_photos,
        hall_titles_js=hall_titles_js,
        services_text_data=_services_text_data(content),
        n_slides=n_slides,
        slide_pct=slide_pct,
    )
