from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app  # noqa: E402


def create_client():
    app = create_app()
    return app.test_client()


def test_list_models_returns_all_entries():
    client = create_client()

    response = client.get("/api/models")

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert {model["id"] for model in data} == {"mdl-1", "mdl-2", "mdl-3", "mdl-4", "mdl-5"}


def test_get_model_returns_single_entry():
    client = create_client()

    response = client.get("/api/models/mdl-1")

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Alpha"
    assert data["category"] == "production"
    assert data["owner"] == "core-team"


def test_get_model_unknown_returns_404():
    client = create_client()

    response = client.get("/api/models/unknown")

    assert response.status_code == 404


def test_download_attachment_returns_file_payload():
    client = create_client()

    response = client.get("/api/models/mdl-1/attachment")

    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert "attachment;" in response.headers["Content-Disposition"]
    assert "alpha.txt" in response.headers["Content-Disposition"]
    assert response.data == b"Alpha model attachment contents"


def test_download_attachment_for_unknown_model_returns_404():
    client = create_client()

    response = client.get("/api/models/unknown/attachment")

    assert response.status_code == 404
