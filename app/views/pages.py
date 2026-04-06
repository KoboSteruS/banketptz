"""
Роуты главных страниц лендинга.
"""
from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import Blueprint, Response, current_app, jsonify, render_template, request, url_for

from app.models import Hall
from app.services.content import (
    build_hall_titles_js,
    build_venue_photos_urls,
    get_merged_site_content,
)
from app.services.vk_notify import parse_peer_ids, send_booking_to_vk
from loguru import logger

pages_bp = Blueprint("pages", __name__)


def _normalize_host(value: str) -> str:
    """Сравнение Host / Origin без учёта регистра и стандартных портов."""
    v = (value or "").strip().lower()
    if ":" in v:
        host, _, port = v.rpartition(":")
        if port in ("80", "443", ""):
            return host
    return v


def _origin_allowed() -> bool:
    """
    Разрешаем POST только с того же хоста, что и страница (защита от CSRF с чужих сайтов).
    За reverse proxy сравниваем Origin с заголовком Host, а не с request.host_url —
    иначе в проде часто 403 (внутренний upstream ≠ публичный домен).
    """
    origin = request.headers.get("Origin")
    if not origin:
        return True
    parsed = urlparse(origin)
    if not parsed.netloc:
        return False
    origin_host = _normalize_host(parsed.netloc)
    req_host = _normalize_host(request.host or "")
    allowed = origin_host == req_host
    if not allowed:
        logger.warning(
            "api/booking: отклонён Origin | origin_host={} req_host={} Host={!r} XFH={!r} scheme={} url={}",
            origin_host,
            req_host,
            request.headers.get("Host"),
            request.headers.get("X-Forwarded-Host"),
            request.scheme,
            request.url,
        )
    return allowed


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


@pages_bp.route("/api/booking", methods=["POST"])
def api_booking():
    """
    Принимает JSON с полями формы бронирования и рассылает текст в VK указанным peer_id.
    """
    if not current_app.config.get("VK_ACCESS_TOKEN"):
        return jsonify({"ok": False, "error": "VK не настроен на сервере"}), 503

    if not _origin_allowed():
        return jsonify({"ok": False, "error": "Недопустимый запрос"}), 403

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Ожидается JSON"}), 400

    # антиспам: скрытое поле «website» не должно заполняться
    if (payload.get("website") or "").strip():
        return jsonify({"ok": True})

    name = (payload.get("name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    if not name or not phone:
        return jsonify({"ok": False, "error": "Укажите имя и телефон"}), 400

    guests = (payload.get("guests") or "").strip()
    date_s = (payload.get("date") or "").strip()
    venue = (payload.get("venue") or "").strip()
    message = (payload.get("message") or "").strip()

    text_lines = [
        "Новая заявка с сайта (бронирование зала)",
        "",
        f"Имя: {name}",
        f"Телефон: {phone}",
        f"Гостей: {guests or '—'}",
        f"Дата: {date_s or '—'}",
        f"Зал: {venue or '—'}",
        "",
        "Комментарий:",
        message or "—",
    ]
    body = "\n".join(text_lines)

    peer_ids = parse_peer_ids(current_app.config.get("VK_NOTIFY_USER_IDS", ""))
    if not peer_ids:
        return jsonify({"ok": False, "error": "Не заданы получатели VK"}), 503

    token = current_app.config["VK_ACCESS_TOKEN"]
    ok, errs = send_booking_to_vk(token, peer_ids, body)
    if not ok:
        logger.error("api/booking: VK ошибки: {}", errs)
        return jsonify(
            {
                "ok": False,
                "error": "Не удалось отправить в VK",
                "details": errs[:5],
            }
        ), 502

    logger.info("api/booking: заявка отправлена в VK, peers={}", peer_ids)
    return jsonify({"ok": True})


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
