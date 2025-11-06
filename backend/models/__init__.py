"""Database models for MakerWorld synchronization."""
from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .entities import Author, Tag, Model, Attachment  # noqa: E402  (import after Base definition)

__all__ = [
    "Base",
    "Author",
    "Tag",
    "Model",
    "Attachment",
]
