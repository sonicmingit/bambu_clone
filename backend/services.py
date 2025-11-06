from datetime import datetime
from typing import Dict, Tuple


class InMemoryDatabase:
    """Simple database abstraction for demo purposes."""

    def __init__(self) -> None:
        self._models: Dict[str, Dict[str, str]] = {
            "mdl-1": {
                "id": "mdl-1",
                "name": "Alpha",
                "description": "Primary production model.",
            },
            "mdl-2": {
                "id": "mdl-2",
                "name": "Beta",
                "description": "Experimental beta model.",
            },
        }

    def list_models(self):
        return list(self._models.values())

    def get_model(self, model_id: str):
        if model_id not in self._models:
            raise KeyError(model_id)
        return self._models[model_id]


class InMemoryStorage:
    """Storage abstraction holding static attachments."""

    def __init__(self) -> None:
        self._attachments: Dict[str, Tuple[str, bytes, str]] = {
            "mdl-1": (
                "alpha.txt",
                b"Alpha model attachment contents",
                "text/plain",
            ),
            "mdl-2": (
                "beta.txt",
                b"Beta model attachment contents",
                "text/plain",
            ),
        }

    def get_attachment(self, model_id: str) -> Tuple[str, bytes, str]:
        if model_id not in self._attachments:
            raise KeyError(model_id)
        return self._attachments[model_id]


class SyncManager:
    """Tracks sync status lifecycle."""

    def __init__(self) -> None:
        self._status: Dict[str, object] = {
            "state": "idle",
            "runs": 0,
            "last_triggered_at": None,
        }

    def trigger(self):
        self._status["state"] = "running"
        self._status["runs"] = int(self._status.get("runs", 0)) + 1
        self._status["last_triggered_at"] = datetime.utcnow().isoformat()
        return self._status

    def status(self):
        return self._status

    def complete(self):
        self._status["state"] = "completed"
        return self._status
