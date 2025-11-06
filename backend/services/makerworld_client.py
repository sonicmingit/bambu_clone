"""Client for interacting with MakerWorld APIs or pages."""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

import requests

LOGGER = logging.getLogger(__name__)


class AuthenticationError(RuntimeError):
    """Raised when the client cannot authenticate."""


class MakerWorldClient:
    """Simple client to fetch model metadata from MakerWorld."""

    BASE_URL = os.getenv("MAKERWORLD_BASE_URL", "https://makerworld.bambulab.com")

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.username = username or os.getenv("MAKERWORLD_USERNAME")
        self.password = password or os.getenv("MAKERWORLD_PASSWORD")
        self._token = token or os.getenv("MAKERWORLD_TOKEN")
        self.session = session or requests.Session()
        self._authenticated = False

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    def authenticate(self) -> None:
        """Authenticate with MakerWorld if credentials are provided."""

        if self._token:
            self.session.headers.setdefault("Authorization", f"Bearer {self._token}")
            self._authenticated = True
            return

        if not self.username or not self.password:
            # Anonymous access may still work for public data.
            LOGGER.debug("No MakerWorld credentials supplied; using anonymous requests")
            self._authenticated = True
            return

        login_url = f"{self.BASE_URL}/api/login"
        response = self.session.post(
            login_url,
            json={"username": self.username, "password": self.password},
            timeout=30,
        )
        if response.status_code >= 400:
            raise AuthenticationError(f"Login failed: {response.status_code} {response.text}")

        data = response.json()
        token = data.get("token")
        if not token:
            raise AuthenticationError("MakerWorld login response missing token")

        self._token = token
        self.session.headers.setdefault("Authorization", f"Bearer {token}")
        self._authenticated = True

    # ------------------------------------------------------------------
    # Fetching helpers
    # ------------------------------------------------------------------
    def fetch_models(
        self,
        page: int = 1,
        per_page: int = 20,
        updated_after: Optional[datetime] = None,
    ) -> Iterable[Dict[str, Any]]:
        """Fetch paginated list of models."""

        self._ensure_authenticated()
        url = f"{self.BASE_URL}/api/models"
        params: Dict[str, Any] = {"page": page, "per_page": per_page}
        if updated_after is not None:
            params["updated_after"] = updated_after.isoformat()

        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()

        try:
            payload = response.json()
        except ValueError:  # pragma: no cover - network fallback
            LOGGER.debug("Non-JSON response received from %s", url)
            return []

        items = payload.get("models") or payload.get("items") or payload
        if isinstance(items, dict):
            items = items.get("models") or items.get("items") or []
        if not isinstance(items, list):
            LOGGER.warning("Unexpected models payload format: %s", type(items))
            return []
        return items

    def fetch_model_details(self, model_id: str) -> Dict[str, Any]:
        """Fetch detailed information about a model."""

        self._ensure_authenticated()
        url = f"{self.BASE_URL}/api/models/{model_id}"
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        try:
            return response.json()
        except ValueError as exc:  # pragma: no cover - network fallback
            raise RuntimeError("MakerWorld model detail response was not JSON") from exc

    def download_file(self, url: str, dest_path: str) -> None:
        """Download a file to a destination path."""

        self._ensure_authenticated()
        LOGGER.debug("Downloading %s to %s", url, dest_path)
        with self.session.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(dest_path, "wb") as file_handle:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file_handle.write(chunk)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _ensure_authenticated(self) -> None:
        if not self._authenticated:
            self.authenticate()

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "MakerWorldClient":
        self._ensure_authenticated()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


__all__ = ["MakerWorldClient", "AuthenticationError"]
