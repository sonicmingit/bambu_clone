"""Background task to ensure stored model files are valid."""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Iterable

from sqlalchemy.orm import Session

from ..models import Model

logger = logging.getLogger(__name__)


def _iter_models(session: Session) -> Iterable[Model]:
    """Yield models from the database, hiding the query implementation."""

    return session.query(Model).all()


def _calculate_checksum(path: Path) -> str:
    """Calculate the SHA256 checksum for a file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_integrity(session: Session, storage_root: str | Path) -> None:
    """Validate that every model file exists and matches the stored checksum."""

    root_path = Path(storage_root)
    for model in _iter_models(session):
        file_path = root_path / model.file_path if not Path(model.file_path).is_absolute() else Path(model.file_path)
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"Model file missing: {file_path}")
            if model.checksum:
                calculated = _calculate_checksum(file_path)
                if calculated != model.checksum:
                    raise ValueError(
                        "Checksum mismatch for model %s: expected %s got %s"
                        % (model.id, model.checksum, calculated)
                    )
        except Exception as exc:  # noqa: BLE001 - we want to log and continue
            logger.exception("Integrity check failed for model_id=%s: %s", model.id, exc)
        else:
            logger.info("Integrity check passed for model_id=%s", model.id)
