from flask import Flask
from flask_cors import CORS

from .config import get_default_config
from .db import SessionLocal, init_db


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_mapping(get_default_config())
    app.config.setdefault("FRONTEND_ORIGIN", "http://127.0.0.1:5173")

    if config_overrides:
        app.config.update(config_overrides)

    from . import models  # noqa: F401

    init_db(app.config["DATABASE_URL"])
    CORS(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}})

    from .routes.documents import documents_bp
    from .routes.health import health_bp
    from .routes.messages import messages_bp
    from .routes.sessions import sessions_bp
    from .routes.uploads import uploads_bp

    app.register_blueprint(documents_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(messages_bp, url_prefix="/api")
    app.register_blueprint(sessions_bp, url_prefix="/api")
    app.register_blueprint(uploads_bp, url_prefix="/api")

    @app.teardown_appcontext
    def cleanup_session(_exception=None):
        SessionLocal.remove()

    return app
