"""
Роуты главных страниц лендинга.
"""
from datetime import datetime, timezone

from flask import Blueprint, Response, render_template, request, url_for

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
    seo = _build_seo_meta(content, halls)
    canonical_url = request.url_root.rstrip("/") + url_for("pages.index")
    image_url = request.url_root.rstrip("/") + url_for("static", filename=seo["image_path"])
    seo_schema = _build_seo_schema(content, halls, canonical_url, image_url, seo)
    return render_template(
        "index.html",
        content=content,
        halls=halls,
        venue_photos=venue_photos,
        hall_titles_js=hall_titles_js,
        services_text_data=_services_text_data(content),
        n_slides=n_slides,
        slide_pct=slide_pct,
        seo=seo,
        seo_schema=seo_schema,
    )


@pages_bp.route("/robots.txt")
def robots_txt() -> Response:
    base = request.url_root.rstrip("/")
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /*/admin/",
        f"Sitemap: {base}{url_for('pages.sitemap_xml')}",
    ]
    return Response("\n".join(lines) + "\n", mimetype="text/plain")


@pages_bp.route("/sitemap.xml")
def sitemap_xml() -> Response:
    base = request.url_root.rstrip("/")
    now_iso = datetime.now(timezone.utc).date().isoformat()
    xml = render_template(
        "sitemap.xml",
        pages=[{"loc": f"{base}{url_for('pages.index')}", "lastmod": now_iso}],
    )
    return Response(xml, mimetype="application/xml")


def _build_seo_meta(content: dict, halls: list[Hall]) -> dict[str, str]:
    header = content.get("header", {})
    hero = content.get("hero", {})
    contacts = content.get("contacts", {})

    brand = (header.get("site_name") or "Банкетные залы").strip()
    city = (header.get("city") or "Петрозаводск").strip()
    title = f"{brand} {city} — аренда банкетных залов для свадеб и мероприятий"
    description = (
        f"{brand} в {city}: выбор банкетных залов для свадеб, юбилеев и корпоративов. "
        f"Вместимость, фото, адреса и бронирование по телефону."
    )

    image_path = hero.get("image") or header.get("logo_path") or "images/logo.png"
    h1 = hero.get("title") or f"{brand} {city}"
    phone = contacts.get("phone1_display") or header.get("phone_display") or ""
    halls_count = str(len(halls))

    return {
        "title": title,
        "description": description,
        "image_path": image_path,
        "h1": h1,
        "city": city,
        "phone": phone,
        "halls_count": halls_count,
    }


def _build_seo_schema(
    content: dict,
    halls: list[Hall],
    canonical_url: str,
    image_url: str,
    seo: dict[str, str],
) -> dict:
    first_address = "Петрозаводск"
    if halls and halls[0].address_line:
        first_address = halls[0].address_line

    return {
        "@context": "https://schema.org",
        "@type": "EventVenue",
        "name": content.get("header", {}).get("site_name", "Банкетные залы"),
        "url": canonical_url,
        "description": seo["description"],
        "telephone": seo["phone"],
        "address": {
            "@type": "PostalAddress",
            "addressLocality": seo["city"],
            "streetAddress": first_address,
            "addressCountry": "RU",
        },
        "image": image_url,
        "priceRange": "₽₽",
        "numberOfRooms": seo["halls_count"],
    }
