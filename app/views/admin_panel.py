"""
Админ-панель: несколько страниц, доступ по токену в пути /<token>/admin/...
"""
import json
import re

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from app.admin_auth import require_admin_token
from app.extensions import db
from app.models import Hall, SiteContent
from app.seed import load_site_defaults_dict
from app.services.admin_texts_form import content_from_texts_form
from app.services.admin_texts_uploads import apply_texts_image_uploads
from app.services.content import (
    deep_merge,
    get_merged_site_content,
    hall_capacity_list,
    hall_photos_paths,
)
from app.utils_upload import allowed_file, save_hall_upload

admin_panel_bp = Blueprint("admin_panel", __name__)

_SLUG_RE = re.compile(r"^[a-z0-9-]+$")


@admin_panel_bp.before_request
def _bind_token() -> None:
    token = request.view_args.get("token") if request.view_args else None
    require_admin_token(token)
    g.admin_token = token


@admin_panel_bp.after_request
def _admin_noindex_headers(response):
    """Запрещаем индексацию всех страниц админки."""
    response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return response


def _token_url(endpoint: str, **kwargs) -> str:
    return url_for(endpoint, token=g.admin_token, **kwargs)


@admin_panel_bp.route("/<token>/admin/")
def dashboard(token: str):
    """Главная админки."""
    hall_count = Hall.query.count()
    return render_template(
        "admin/dashboard.html",
        hall_count=hall_count,
        token_url=_token_url,
    )


@admin_panel_bp.route("/<token>/admin/texts/empty", methods=["POST"])
def texts_reset_empty(token: str):
    """Сброс контента к файлу site_defaults.json (не трогает залы)."""
    data = load_site_defaults_dict()
    row = SiteContent.query.filter_by(key="main").first()
    if row:
        row.json_value = json.dumps(data, ensure_ascii=False)
    else:
        db.session.add(
            SiteContent(key="main", json_value=json.dumps(data, ensure_ascii=False))
        )
    db.session.commit()
    flash("Контент сброшен к значениям по умолчанию из файла.", "success")
    return redirect(_token_url("admin_panel.texts_edit"))


@admin_panel_bp.route("/<token>/admin/texts/", methods=["GET", "POST"])
def texts_edit(token: str):
    """Редактирование контента страницы (форма полей + placeholder из дефолтов)."""
    defaults = load_site_defaults_dict()
    row = SiteContent.query.filter_by(key="main").first()
    if request.method == "POST":
        parsed = content_from_texts_form(request, defaults)
        for w in apply_texts_image_uploads(request, parsed):
            flash(w, "warning")
        merged = deep_merge(defaults, parsed)
        if row:
            row.json_value = json.dumps(merged, ensure_ascii=False)
        else:
            db.session.add(
                SiteContent(
                    key="main",
                    json_value=json.dumps(merged, ensure_ascii=False),
                )
            )
        db.session.commit()
        flash("Контент сохранён.", "success")
        return redirect(_token_url("admin_panel.texts_edit"))

    content = get_merged_site_content()
    return render_template(
        "admin/texts_edit.html",
        content=content,
        defaults=defaults,
        token_url=_token_url,
    )


@admin_panel_bp.route("/<token>/admin/halls/")
def halls_list(token: str):
    halls = Hall.query.order_by(Hall.sort_order, Hall.title_short).all()
    return render_template(
        "admin/halls_list.html",
        halls=halls,
        token_url=_token_url,
    )


@admin_panel_bp.route("/<token>/admin/halls/new/", methods=["GET", "POST"])
def hall_new(token: str):
    if request.method == "POST":
        err = _validate_hall_form(request)
        if err:
            flash(err, "error")
            return render_template(
                "admin/hall_form.html",
                hall=None,
                capacity_lines_text="",
                photos_lines_text="",
                token_url=_token_url,
            )
        hall, upload_warnings = _hall_from_form(request, None)
        for w in upload_warnings:
            flash(w, "warning")
        db.session.add(hall)
        db.session.commit()
        flash("Зал добавлен.", "success")
        return redirect(_token_url("admin_panel.halls_list"))
    return render_template(
        "admin/hall_form.html",
        hall=None,
        capacity_lines_text="",
        photos_lines_text="",
        token_url=_token_url,
    )


@admin_panel_bp.route("/<token>/admin/halls/<hall_id>/edit/", methods=["GET", "POST"])
def hall_edit(token: str, hall_id: str):
    hall = Hall.query.get_or_404(hall_id)
    if request.method == "POST":
        err = _validate_hall_form(request, hall.id)
        if err:
            flash(err, "error")
            return render_template(
                "admin/hall_form.html",
                hall=hall,
                capacity_lines_text="\n".join(hall_capacity_list(hall)),
                photos_lines_text="\n".join(hall_photos_paths(hall)),
                token_url=_token_url,
            )
        _, upload_warnings = _hall_from_form(request, hall)
        for w in upload_warnings:
            flash(w, "warning")
        db.session.commit()
        flash("Зал сохранён.", "success")
        return redirect(_token_url("admin_panel.halls_list"))
    return render_template(
        "admin/hall_form.html",
        hall=hall,
        capacity_lines_text="\n".join(hall_capacity_list(hall)),
        photos_lines_text="\n".join(hall_photos_paths(hall)),
        token_url=_token_url,
    )


@admin_panel_bp.route("/<token>/admin/halls/<hall_id>/delete/", methods=["POST"])
def hall_delete(token: str, hall_id: str):
    hall = Hall.query.get_or_404(hall_id)
    db.session.delete(hall)
    db.session.commit()
    flash("Зал удалён.", "success")
    return redirect(_token_url("admin_panel.halls_list"))


def _validate_hall_form(request, exclude_id: str | None = None) -> str | None:
    slug = (request.form.get("slug") or "").strip().lower()
    if not slug or not _SLUG_RE.match(slug):
        return "Slug: только латиница, цифры и дефис (например sverdlov)."
    q = Hall.query.filter_by(slug=slug)
    if exclude_id:
        q = q.filter(Hall.id != exclude_id)
    if q.first():
        return "Зал с таким slug уже есть."
    return None


def _parse_capacity_lines(text: str) -> list[str]:
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    return lines[:10] if lines else ["", "", ""]


def _parse_photos_lines(text: str) -> list[str]:
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]


def _gallery_upload_paths_and_warnings(request) -> tuple[list[str], list[str]]:
    """Сохраняет все файлы из поля gallery_photos (multiple) в uploads/halls/."""
    paths: list[str] = []
    warnings: list[str] = []
    for f in request.files.getlist("gallery_photos"):
        if not f or not f.filename:
            continue
        if not allowed_file(f.filename):
            warnings.append(f"Модалка: файл «{f.filename}» пропущен (нужны PNG, JPG, JPEG, WebP, GIF).")
            continue
        p = save_hall_upload(f)
        if p:
            paths.append(p)
    return paths, warnings


def _hall_from_form(request, existing: Hall | None) -> tuple[Hall, list[str]]:
    slug = (request.form.get("slug") or "").strip().lower()
    cap = _parse_capacity_lines(request.form.get("capacity_lines") or "")
    photos_text = request.form.get("photos_json") or ""
    photos_from_text = _parse_photos_lines(photos_text)
    uploaded_paths, upload_warnings = _gallery_upload_paths_and_warnings(request)
    photos = photos_from_text + uploaded_paths

    uf_g = request.files.get("image_gallery")
    uf_d = request.files.get("image_detail")
    path_g = save_hall_upload(uf_g) if uf_g else None
    path_d = save_hall_upload(uf_d) if uf_d else None

    if existing:
        h = existing
        h.slug = slug
        h.sort_order = int(request.form.get("sort_order") or 0)
        h.title_short = (request.form.get("title_short") or "").strip() or h.title_short
        h.title_full = (request.form.get("title_full") or "").strip() or h.title_full
        h.meta_line = (request.form.get("meta_line") or "").strip()
        h.address_line = (request.form.get("address_line") or "").strip()
        h.maps_link = (request.form.get("maps_link") or "").strip()
        h.capacity_lines = json.dumps(cap, ensure_ascii=False)
        if path_g:
            h.image_gallery = path_g
        elif request.form.get("image_gallery_path"):
            h.image_gallery = request.form.get("image_gallery_path", "").strip()
        if path_d:
            h.image_detail = path_d
        elif request.form.get("image_detail_path"):
            h.image_detail = request.form.get("image_detail_path", "").strip()
        h.photos_json = json.dumps(photos, ensure_ascii=False)
        h.is_active = request.form.get("is_active") == "1"
        return h, upload_warnings

    ig = path_g or (request.form.get("image_gallery_path") or "").strip()
    idt = path_d or (request.form.get("image_detail_path") or "").strip()
    if not photos:
        photos = [ig, idt] if ig or idt else []

    return (
        Hall(
            slug=slug,
            sort_order=int(request.form.get("sort_order") or 0),
            title_short=(request.form.get("title_short") or "").strip() or "Зал",
            title_full=(request.form.get("title_full") or "").strip() or "ЗАЛ",
            meta_line=(request.form.get("meta_line") or "").strip(),
            capacity_lines=json.dumps(cap, ensure_ascii=False),
            address_line=(request.form.get("address_line") or "").strip(),
            maps_link=(request.form.get("maps_link") or "").strip(),
            image_gallery=ig,
            image_detail=idt,
            photos_json=json.dumps(photos, ensure_ascii=False),
            is_active=request.form.get("is_active") == "1",
        ),
        upload_warnings,
    )
