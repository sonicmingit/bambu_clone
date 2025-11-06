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
                "category": "production",
                "owner": "core-team",
            },
            "mdl-2": {
                "id": "mdl-2",
                "name": "Beta",
                "description": "Experimental beta model.",
                "category": "experiment",
                "owner": "labs",
            },
            "mdl-3": {
                "id": "mdl-3",
                "name": "Gamma",
                "description": "Regional recommendation model tuned for APAC.",
                "category": "regional",
                "owner": "growth",
            },
            "mdl-4": {
                "id": "mdl-4",
                "name": "Delta",
                "description": "Legacy fallback model kept for compatibility.",
                "category": "legacy",
                "owner": "platform",
            },
            "mdl-5": {
                "id": "mdl-5",
                "name": "Epsilon",
                "description": "Offline batch scoring pipeline.",
                "category": "batch",
                "owner": "data-engineering",
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
            "mdl-3": (
                "gamma.csv",
                b"id,score\nuser-1,0.87\nuser-2,0.91\n",
                "text/csv",
            ),
            "mdl-4": (
                "delta.json",
                b"{\"status\": \"deprecated\", \"sunset_at\": \"2025-03-01\"}",
                "application/json",
            ),
            "mdl-5": (
                "epsilon.log",
                b"2024-04-01T00:00:00Z pipeline completed successfully",
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
