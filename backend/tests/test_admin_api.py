from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app  # noqa: E402

ADMIN_TOKEN = "secret-token"


def create_client():
    app = create_app()
    return app.test_client()


def test_sync_requires_token():
    client = create_client()

    response = client.post("/api/admin/sync")

    assert response.status_code == 401


def test_sync_trigger_and_status_flow():
    client = create_client()

    trigger_response = client.post(
        "/api/admin/sync", headers={"X-Admin-Token": ADMIN_TOKEN}
    )
    assert trigger_response.status_code == 202
    trigger_payload = trigger_response.get_json()
    assert trigger_payload["state"] == "running"
    assert trigger_payload["runs"] == 1

    status_response = client.get(
        "/api/admin/sync", headers={"X-Admin-Token": ADMIN_TOKEN}
    )
    assert status_response.status_code == 200
    status_payload = status_response.get_json()
    assert status_payload["state"] == "running"
    assert status_payload["runs"] == 1


def test_sync_status_requires_valid_token():
    client = create_client()

    response = client.get(
        "/api/admin/sync", headers={"X-Admin-Token": "invalid"}
    )

    assert response.status_code == 401
