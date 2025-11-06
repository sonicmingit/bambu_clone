"""Synchronization tasks that fetch MakerWorld models and persist them."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Union

from backend.database import engine, session_scope
from backend.models import Attachment, Author, Base, Model, Tag
from backend.services.makerworld_client import MakerWorldClient

LOGGER = logging.getLogger(__name__)

# Ensure tables exist on module import so that scheduler jobs run without manual setup.
Base.metadata.create_all(bind=engine)


def sync_models(
    *,
    client: Optional[MakerWorldClient] = None,
    pages: int = 1,
    per_page: int = 20,
    updated_after: Optional[datetime] = None,
    download_files: bool = True,
    storage_root: Optional[Union[Path, str]] = None,
) -> None:
    """Synchronize MakerWorld models into the database."""

    storage_path = Path(storage_root) if storage_root else Path("storage/models")
    storage_path.mkdir(parents=True, exist_ok=True)

    managed_client = client is None
    client = client or MakerWorldClient()

    try:
        for page in range(1, pages + 1):
            models_page = list(client.fetch_models(page=page, per_page=per_page, updated_after=updated_after))
            if not models_page:
                LOGGER.info("No models returned for page %s; stopping pagination", page)
                break

            for summary in models_page:
                model_id = str(summary.get("id"))
                if not model_id:
                    LOGGER.warning("Skipping model without identifier: %s", summary)
                    continue

                details = client.fetch_model_details(model_id)
                _persist_model(details, download_files=download_files, storage_root=storage_path, client=client)
    finally:
        if managed_client:
            client.close()


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def _persist_model(
    payload: Dict[str, Any],
    *,
    download_files: bool,
    storage_root: Path,
    client: MakerWorldClient,
) -> None:
    model_id = str(payload.get("id"))
    if not model_id:
        LOGGER.warning("Received model payload without ID: %s", payload)
        return

    with session_scope() as session:
        author_info = payload.get("author") or {}
        author = None
        author_id = author_info.get("id")
        if author_id:
            author = session.get(Author, str(author_id))
            if author is None:
                author = Author(
                    id=str(author_id),
                    display_name=author_info.get("displayName")
                    or author_info.get("name")
                    or author_info.get("username")
                    or "Unknown",
                    username=author_info.get("username"),
                    profile_url=author_info.get("profileUrl"),
                )
                session.add(author)
            else:
                author.display_name = author_info.get("displayName") or author.display_name
                author.username = author_info.get("username") or author.username
                author.profile_url = author_info.get("profileUrl") or author.profile_url

        model = session.get(Model, model_id)
        if model is None:
            model = Model(id=model_id, name=payload.get("name") or payload.get("title") or "Unnamed")
            session.add(model)
        model.name = payload.get("name") or payload.get("title") or model.name
        model.description = payload.get("description")
        model.source_url = payload.get("url") or payload.get("sourceUrl")
        model.thumbnail_url = payload.get("thumbnail") or payload.get("thumbnailUrl")
        model.updated_at = _parse_datetime(payload.get("updatedAt") or payload.get("updated_at"))
        model.created_at = _parse_datetime(payload.get("createdAt") or payload.get("created_at"))
        model.author = author

        # Tags
        tags_payload: Iterable[Dict[str, Any]] = payload.get("tags") or []
        model.tags.clear()
        for tag_payload in tags_payload:
            tag_id = str(tag_payload.get("id") or tag_payload.get("slug") or tag_payload.get("name"))
            if not tag_id:
                continue
            tag = session.get(Tag, tag_id)
            if tag is None:
                tag = Tag(
                    id=tag_id,
                    name=tag_payload.get("name") or tag_payload.get("slug") or tag_id,
                    slug=tag_payload.get("slug"),
                )
                session.add(tag)
            model.tags.append(tag)

        # Attachments
        attachments_payload: Iterable[Dict[str, Any]] = payload.get("attachments") or payload.get("files") or []
        seen_ids: set[str] = set()

        for attachment_payload in attachments_payload:
            attachment_id = str(attachment_payload.get("id") or attachment_payload.get("fileId") or attachment_payload.get("uuid"))
            if not attachment_id:
                LOGGER.debug("Skipping attachment without ID for model %s", model_id)
                continue

            seen_ids.add(attachment_id)
            attachment = session.get(Attachment, attachment_id)
            if attachment is None:
                attachment = Attachment(id=attachment_id, model=model, filename="")
                session.add(attachment)

            attachment.model = model
            attachment.filename = attachment_payload.get("filename") or attachment_payload.get("name") or attachment.filename
            attachment.filetype = attachment_payload.get("filetype") or attachment_payload.get("type")
            attachment.size = attachment_payload.get("size")
            attachment.checksum = attachment_payload.get("checksum") or attachment_payload.get("md5")
            attachment.download_url = attachment_payload.get("downloadUrl") or attachment_payload.get("url")

            if download_files and attachment.download_url:
                local_dir = storage_root / model_id
                local_dir.mkdir(parents=True, exist_ok=True)
                local_path = local_dir / (attachment.filename or f"{attachment.id}")
                if local_path.exists():
                    attachment.local_path = str(local_path)
                else:
                    try:
                        client.download_file(attachment.download_url, str(local_path))
                        attachment.local_path = str(local_path)
                    except Exception as exc:  # pragma: no cover - network fallback
                        LOGGER.exception("Failed to download attachment %s: %s", attachment.download_url, exc)

        # Remove attachments no longer present
        for attachment in list(model.attachments):
            if attachment.id not in seen_ids:
                session.delete(attachment)

        LOGGER.info("Persisted model %s (%s attachments)", model.name, len(model.attachments))


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    if isinstance(value, str):
        try:
            if value.endswith("Z"):
                value = value.replace("Z", "+00:00")
            return datetime.fromisoformat(value)
        except ValueError:  # pragma: no cover - best effort parse
            LOGGER.debug("Could not parse datetime value: %s", value)
            return None
    return None
