"""Flask routes exposing read-only model data and attachments."""

from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, List

from flask import Blueprint, abort, current_app, jsonify, send_file

from ...services import InMemoryDatabase, InMemoryStorage

router = Blueprint("models", __name__, url_prefix="/models")


def _get_database() -> InMemoryDatabase:
    """Retrieve the configured database service or fail with a 500 error."""

    database = current_app.config.get("DATABASE")
    if not isinstance(database, InMemoryDatabase):
        abort(500, description="Database service not configured.")
    return database


def _get_storage() -> InMemoryStorage:
    """Retrieve the configured storage service or fail with a 500 error."""

    storage = current_app.config.get("STORAGE")
    if not isinstance(storage, InMemoryStorage):
        abort(500, description="Storage service not configured.")
    return storage


@router.get("")
def list_models():
    """Return the list of available models."""

    database = _get_database()
    models: List[Dict[str, Any]] = database.list_models()
    return jsonify(models)


@router.get("/<model_id>")
def get_model(model_id: str):
    """Return metadata for a single model or a 404 when missing."""

    database = _get_database()
    try:
        model: Dict[str, Any] = database.get_model(model_id)
    except KeyError:
        abort(404, description="Model not found.")
    return jsonify(model)


@router.get("/<model_id>/attachment")
def download_attachment(model_id: str):
    """Return the attachment associated with a model as a download."""

    storage = _get_storage()
    try:
        filename, payload, mimetype = storage.get_attachment(model_id)
    except KeyError:
        abort(404, description="Attachment not found.")

    buffer = BytesIO(payload)
    buffer.seek(0)
    return send_file(buffer, mimetype=mimetype, as_attachment=True, download_name=filename)
