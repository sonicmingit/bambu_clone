"""SQLAlchemy models representing MakerWorld entities."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


model_tags = Table(
    "model_tags",
    Base.metadata,
    Column("model_id", ForeignKey("models.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Author(Base):
    """Model author."""

    __tablename__ = "authors"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    profile_url: Mapped[Optional[str]] = mapped_column(String(500))

    models: Mapped[list["Model"]] = relationship("Model", back_populates="author", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Author(id={self.id!r}, display_name={self.display_name!r})"


class Tag(Base):
    """Model tag."""

    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[Optional[str]] = mapped_column(String(255))

    models: Mapped[list["Model"]] = relationship("Model", secondary=model_tags, back_populates="tags")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Tag(id={self.id!r}, name={self.name!r})"


class Model(Base):
    """3D model metadata."""

    __tablename__ = "models"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text())
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    author_id: Mapped[Optional[str]] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Optional[Author]] = relationship("Author", back_populates="models")

    tags: Mapped[list[Tag]] = relationship("Tag", secondary=model_tags, back_populates="models")
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment",
        back_populates="model",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Model(id={self.id!r}, name={self.name!r})"


class Attachment(Base):
    """Model file attachment."""

    __tablename__ = "attachments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    model_id: Mapped[str] = mapped_column(String(64), ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filetype: Mapped[Optional[str]] = mapped_column(String(50))
    size: Mapped[Optional[int]] = mapped_column(Integer())
    checksum: Mapped[Optional[str]] = mapped_column(String(255))
    download_url: Mapped[Optional[str]] = mapped_column(String(500))
    local_path: Mapped[Optional[str]] = mapped_column(String(500))

    model: Mapped[Model] = relationship("Model", back_populates="attachments")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Attachment(id={self.id!r}, filename={self.filename!r})"
