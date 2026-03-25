"""
Сборка словаря контента сайта из POST-формы админки «Тексты».
"""
from typing import Any

from flask import Request


def _get(request: Request, key: str) -> str:
    return (request.form.get(key) or "").strip()


def content_from_texts_form(request: Request, defaults: dict[str, Any]) -> dict[str, Any]:
    """Полный объект контента по полям формы (пустые строки сохраняются как есть)."""
    sv = defaults["services"]
    slide_count = len(sv.get("slides", []))
    slides = []
    for i in range(slide_count):
        slides.append(
            {
                "img": _get(request, f"slide_{i}_img"),
                "alt": _get(request, f"slide_{i}_alt"),
                "title": _get(request, f"slide_{i}_title"),
                "desc": _get(request, f"slide_{i}_desc"),
                "btn": _get(request, f"slide_{i}_btn"),
                "nav_label": _get(request, f"slide_{i}_nav_label"),
                "nav_aria": _get(request, f"slide_{i}_nav_aria"),
            }
        )

    rv = defaults["reasons"]
    ritems = rv.get("items", [])
    reason_items = []
    for i in range(len(ritems)):
        reason_items.append(
            {
                "title": _get(request, f"reason_{i}_title"),
                "desc": _get(request, f"reason_{i}_desc"),
            }
        )

    vs = defaults["venues_section"]
    summ = vs.get("summary", [])
    summary = []
    for i in range(len(summ)):
        summary.append(
            {
                "title": _get(request, f"vs_sum_{i}_title"),
                "text": _get(request, f"vs_sum_{i}_text"),
            }
        )

    mn = defaults["menu"]
    cli = mn.get("card_list_items", [])
    card_lines = []
    for i in range(len(cli)):
        card_lines.append(_get(request, f"menu_li_{i}"))

    return {
        "header": {
            "site_name": _get(request, "header_site_name"),
            "city": _get(request, "header_city"),
            "logo_path": _get(request, "header_logo_path"),
            "phone_display": _get(request, "header_phone_display"),
            "phone_href": _get(request, "header_phone_href"),
            "mobile_phone_display": _get(request, "header_mobile_phone_display"),
        },
        "hero": {
            "image": _get(request, "hero_image"),
            "title": _get(request, "hero_title"),
            "lead": _get(request, "hero_lead"),
            "cta_book": _get(request, "hero_cta_book"),
            "cta_venues": _get(request, "hero_cta_venues"),
        },
        "services": {
            "section_title": _get(request, "serv_section_title"),
            "section_subtitle": _get(request, "serv_section_subtitle"),
            "slides": slides,
            "note_title": _get(request, "serv_note_title"),
            "note_text": _get(request, "serv_note_text"),
        },
        "reasons": {
            "title": _get(request, "reasons_title"),
            "subtitle": _get(request, "reasons_subtitle"),
            "image": _get(request, "reasons_image"),
            "items": reason_items,
        },
        "venues_section": {
            "heading": _get(request, "vs_heading"),
            "link_href": _get(request, "vs_link_href"),
            "link_text": _get(request, "vs_link_text"),
            "summary": summary,
        },
        "menu": {
            "title": _get(request, "menu_title"),
            "food_image": _get(request, "menu_food_image"),
            "menu_doc_url": _get(request, "menu_doc_url"),
            "card_list_title": _get(request, "menu_card_list_title"),
            "card_list_items": card_lines,
            "card_list_text": _get(request, "menu_card_list_text"),
            "corkage_image": _get(request, "menu_corkage_image"),
            "corkage_title": _get(request, "menu_corkage_title"),
            "corkage_text": _get(request, "menu_corkage_text"),
            "degust_title": _get(request, "menu_degust_title"),
            "degust_text": _get(request, "menu_degust_text"),
        },
        "contacts": {
            "section_title": _get(request, "ct_section_title"),
            "section_subtitle": _get(request, "ct_section_subtitle"),
            "form_title": _get(request, "ct_form_title"),
            "contacts_title": _get(request, "ct_contacts_title"),
            "phone_label": _get(request, "ct_phone_label"),
            "phone1_display": _get(request, "ct_phone1_display"),
            "phone1_href": _get(request, "ct_phone1_href"),
            "phone2_display": _get(request, "ct_phone2_display"),
            "phone2_href": _get(request, "ct_phone2_href"),
            "hours": _get(request, "ct_hours"),
            "location_label": _get(request, "ct_location_label"),
            "location_text": _get(request, "ct_location_text"),
            "map_title": _get(request, "ct_map_title"),
            "map_embed_url": _get(request, "ct_map_embed_url"),
            "map_iframe_title": _get(request, "ct_map_iframe_title"),
        },
        "footer": {
            "brand_name": _get(request, "ft_brand_name"),
            "tagline": _get(request, "ft_tagline"),
            "vk_url": _get(request, "ft_vk_url"),
            "copy": _get(request, "ft_copy"),
            "credit_html": _get(request, "ft_credit_html"),
        },
    }
