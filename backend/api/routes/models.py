from io import BytesIO
from typing import Any, Dict, List

from flask import Blueprint, Response, abort, current_app, jsonify, send_file

from ...services import InMemoryDatabase, InMemoryStorage

router = Blueprint("models", __name__, url_prefix="/models")


def get_database() -> InMemoryDatabase:
    database = current_app.config.get("DATABASE")
    if database is None:
        abort(500, description="Database dependency not configured.")
    return database


def get_storage() -> InMemoryStorage:
    storage = current_app.config.get("STORAGE")
    if storage is None:
        abort(500, description="Storage dependency not configured.")
    return storage


@router.get("")
def list_models() -> Response:
    database = get_database()
    models: List[Dict[str, Any]] = database.list_models()
    return jsonify(models)


@router.get("/<model_id>")
def get_model(model_id: str) -> Response:
    database = get_database()
    try:
        model = database.get_model(model_id)
    except KeyError:
        abort(404, description="Model not found")
    return jsonify(model)


@router.get("/<model_id>/attachment")
def download_attachment(model_id: str):
    storage = get_storage()
    try:
        filename, payload, media_type = storage.get_attachment(model_id)
    except KeyError:
        abort(404, description="Model not found")

    file_obj = BytesIO(payload)
    file_obj.seek(0)
    return send_file(
        file_obj,
        mimetype=media_type,
        as_attachment=True,
        download_name=filename,
    )
