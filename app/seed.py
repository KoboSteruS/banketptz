"""
Первичное заполнение БД при пустых таблицах.
"""
import json
from pathlib import Path

from app.extensions import db
from app.models import Hall, SiteContent


def _defaults_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "site_defaults.json"


def load_site_defaults_dict() -> dict:
    return json.loads(_defaults_path().read_text(encoding="utf-8"))


def seed_if_empty() -> None:
    """Создаёт записи по умолчанию, если БД пустая."""
    if SiteContent.query.filter_by(key="main").first() is None:
        data = load_site_defaults_dict()
        db.session.add(
            SiteContent(key="main", json_value=json.dumps(data, ensure_ascii=False))
        )

    if Hall.query.count() == 0:
        halls = [
            {
                "slug": "sverdlov",
                "sort_order": 0,
                "title_short": "СвердловЪ",
                "title_full": "ЗАЛ СВЕРДЛОВЪ",
                "meta_line": "до 100 гостей",
                "capacity_lines": [
                    "Банкетная рассадка – до 100 гостей",
                    "Фуршет – до 100 человек",
                    "Улица Свердлова, 7",
                ],
                "address_line": "Улица Свердлова, 7",
                "maps_link": "https://www.google.com/maps/search/%D0%BD%D0%B0%D0%B1%D0%B5%D1%80%D0%B5%D0%B6%D0%BD%D0%B0%D1%8F+%D0%9E%D0%BD%D0%B5%D0%B6%D1%81%D0%BA%D0%BE%D0%B3%D0%BE+%D0%BE%D0%B7%D0%B5%D1%80%D0%B0+%D0%9F%D0%B5%D1%82%D1%80%D0%BE%D0%B7%D0%B0%D0%B2%D0%BE%D0%B4%D1%81%D0%BA",
                "image_gallery": "images/Sverdlov/Sverdlov.jpg",
                "image_detail": "images/Sverdlov/Sverdlov2.jpg",
                "photos_json": [
                    "images/Sverdlov/Sverdlov.jpg",
                    "images/Sverdlov/Sverdlov2.jpg",
                ],
            },
            {
                "slug": "serebryany",
                "sort_order": 1,
                "title_short": "Серебряный",
                "title_full": "ЗАЛ СЕРЕБРЯНЫЙ",
                "meta_line": "10–30 гостей",
                "capacity_lines": [
                    "Банкетная рассадка – 10–30 гостей",
                    "Фуршет – до 30 человек",
                    "Набережная Варкауса, 35",
                ],
                "address_line": "Набережная Варкауса, 35",
                "maps_link": "https://www.google.com/maps/search/%D0%BD%D0%B0%D0%B1%D0%B5%D1%80%D0%B5%D0%B6%D0%BD%D0%B0%D1%8F+%D0%9F%D0%B5%D1%82%D1%80%D0%BE%D0%B7%D0%B0%D0%B2%D0%BE%D0%B4%D1%81%D0%BA",
                "image_gallery": "images/Serebro/Serebro.jpg",
                "image_detail": "images/Serebro/Serebro2.jpg",
                "photos_json": [
                    "images/Serebro/Serebro.jpg",
                    "images/Serebro/Serebro2.jpg",
                ],
            },
            {
                "slug": "tradicia",
                "sort_order": 2,
                "title_short": "Традиция",
                "title_full": "ЗАЛ «ТРАДИЦИЯ»",
                "meta_line": "50–70 гостей",
                "capacity_lines": [
                    "Банкетная рассадка – 50–70 гостей",
                    "Фуршет – до 70 человек",
                    "Балтийская улица, 5Б",
                ],
                "address_line": "Балтийская улица, 5Б",
                "maps_link": "https://www.google.com/maps/search/%D0%91%D0%B0%D0%BD%D0%BA%D0%B5%D1%82%D0%BD%D1%8B%D0%B9+%D0%B7%D0%B0%D0%BB+%D0%A2%D1%80%D0%B0%D0%B4%D0%B8%D1%86%D0%B8%D1%8F+%D0%9F%D0%B5%D1%82%D1%80%D0%BE%D0%B7%D0%B0%D0%B2%D0%BE%D0%B4%D1%81%D0%BA",
                "image_gallery": "images/Tradicia/Tradicia.jpg",
                "image_detail": "images/Tradicia/Tradition.jpg",
                "photos_json": [
                    "images/Tradicia/Tradicia.jpg",
                    "images/Tradicia/Tradition.jpg",
                ],
            },
            {
                "slug": "gogolya",
                "sort_order": 3,
                "title_short": "На Гоголя",
                "title_full": "ЗАЛ НА ГОГОЛЯ",
                "meta_line": "до 70 гостей",
                "capacity_lines": [
                    "Банкетная рассадка – до 70 гостей",
                    "Фуршет – до 70 человек",
                    "Улица Гоголя, 21а",
                ],
                "address_line": "Улица Гоголя, 21а",
                "maps_link": "https://www.google.com/maps/search/%D1%83%D0%BB+%D0%93%D0%BE%D0%B3%D0%BE%D0%BB%D1%8F+%D0%9F%D0%B5%D1%82%D1%80%D0%BE%D0%B7%D0%B0%D0%B2%D0%BE%D0%B4%D1%81%D0%BA",
                "image_gallery": "images/Gogolya/gogolya.jpg",
                "image_detail": "images/Gogolya/Gogolya2.jpg",
                "photos_json": [
                    "images/Gogolya/gogolya.jpg",
                    "images/Gogolya/Gogolya2.jpg",
                ],
            },
            {
                "slug": "cascad",
                "sort_order": 4,
                "title_short": "Каскад",
                "title_full": "ЗАЛ КАСКАД",
                "meta_line": "до 30 гостей",
                "capacity_lines": [
                    "Банкетная рассадка – до 30 гостей",
                    "Фуршет – до 30 человек",
                    "Древлянка, пр. Афанасьева, 2",
                ],
                "address_line": "ЖК Каскад Проезд Алексея Афанасьева, 2",
                "maps_link": "https://www.google.com/maps/search/%D0%BF%D1%80%D0%BE%D0%B5%D0%B7%D0%B4+%D0%90%D0%BB%D0%B5%D0%BA%D1%81%D0%B5%D1%8F+%D0%90%D1%84%D0%B0%D0%BD%D0%B0%D1%81%D1%8C%D0%B5%D0%B2%D0%B0+2+%D0%9F%D0%B5%D1%82%D1%80%D0%BE%D0%B7%D0%B0%D0%B2%D0%BE%D0%B4%D1%81%D0%BA",
                "image_gallery": "images/Cascad/Kascad.jpg",
                "image_detail": "images/Cascad/Caskad.jpg",
                "photos_json": [
                    "images/Cascad/Kaskad.jpg",
                    "images/Cascad/Caskad.jpg",
                ],
            },
            {
                "slug": "room",
                "sort_order": 5,
                "title_short": "Room",
                "title_full": "ЗАЛ ROOM",
                "meta_line": "до 40 гостей",
                "capacity_lines": [
                    "Банкетная рассадка – до 40 гостей",
                    "Фуршет – до 40 человек",
                    "Улица Максима Горького, 6",
                ],
                "address_line": "Улица Максима Горького, 6",
                "maps_link": "https://www.google.com/maps/place/ROOM-%D0%BA%D0%B0%D1%84%D0%B5/@61.7852585,34.358432,17z/data=!3m1!4b1!4m6!3m5!1s0x46a1ec46bbe2ed3d:0x76eb8a4a2b6184b4!8m2!3d61.7852585!4d34.358432!16s%2Fg%2F11fxcd4r7d?hl=ru&entry=ttu&g_ep=EgoyMDI2MDIyNS4wIKXMDSoASAFQAw%3D%3D",
                "image_gallery": "images/Cascad/Room.jpg",
                "image_detail": "images/Cascad/Room1.jpg",
                "photos_json": [
                    "images/Cascad/Room.jpg",
                    "images/Cascad/Room1.jpg",
                ],
            },
        ]
        for h in halls:
            photos = h.pop("photos_json")
            cap = h.pop("capacity_lines")
            db.session.add(
                Hall(
                    **h,
                    capacity_lines=json.dumps(cap, ensure_ascii=False),
                    photos_json=json.dumps(photos, ensure_ascii=False),
                )
            )

    db.session.commit()
