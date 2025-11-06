from flask import Blueprint, abort, current_app, jsonify, request

from ...services import SyncManager

router = Blueprint("admin", __name__, url_prefix="/api/admin")


def get_sync_manager() -> SyncManager:
    manager = current_app.config.get("SYNC_MANAGER")
    if manager is None:
        abort(500, description="Sync manager not configured.")
    return manager


def get_expected_token() -> str:
    token = current_app.config.get("ADMIN_TOKEN")
    if token is None:
        abort(500, description="Admin token not configured.")
    return token


def require_token() -> None:
    expected_token = get_expected_token()
    provided_token = request.headers.get("X-Admin-Token")
    if expected_token != provided_token:
        abort(401, description="Invalid or missing admin token.")


@router.post("/sync")
def trigger_sync():
    require_token()
    sync_manager = get_sync_manager()
    status = sync_manager.trigger()
    return jsonify(status), 202


@router.get("/sync")
def get_sync_status():
    require_token()
    sync_manager = get_sync_manager()
    status = sync_manager.status()
    return jsonify(status)
