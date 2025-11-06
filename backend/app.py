try:  # Prefer the real Flask package when available.
    from flask import Flask
except ModuleNotFoundError:  # pragma: no cover - fallback for local stub usage
    from flask_stub import Flask

from .api.routes import admin, models
from .services import InMemoryDatabase, InMemoryStorage, SyncManager


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["DATABASE"] = InMemoryDatabase()
    app.config["STORAGE"] = InMemoryStorage()
    app.config["SYNC_MANAGER"] = SyncManager()
    app.config["ADMIN_TOKEN"] = "secret-token"

    app.register_blueprint(models.router)
    app.register_blueprint(admin.router)

    return app


app = create_app()
