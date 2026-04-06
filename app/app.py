"""
Точка входа Flask-приложения Banket.
"""
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

from app.config import Config
from app.extensions import db
from app.seed import seed_if_empty
from app.views.admin_panel import admin_panel_bp
from app.views.pages import pages_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    # За nginx / другим reverse proxy: корректные Host, Scheme, url_for
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
    Path(app.config["INSTANCE_PATH"]).mkdir(parents=True, exist_ok=True)
    (Path(app.root_path) / "static" / "uploads" / "halls").mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    with app.app_context():
        db.create_all()
        seed_if_empty()

    app.register_blueprint(pages_bp)
    app.register_blueprint(admin_panel_bp)

    def _hall_capacity_filter(hall):
        from app.services.content import hall_capacity_list

        return hall_capacity_list(hall)

    app.jinja_env.filters["hall_capacity"] = _hall_capacity_filter
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
