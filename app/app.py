"""
Точка входа Flask-приложения Banket.
"""
from flask import Flask

from app.views.pages import pages_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(pages_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
