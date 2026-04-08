from flask import Flask

from .config import get_default_config


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_mapping(get_default_config())

    if config_overrides:
        app.config.update(config_overrides)

    from .routes.health import health_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    return app
