"""Tables storing detailed download and favorite actions."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base


class DownloadRecord(Base):
    """A record of a model download event."""

    __tablename__ = "download_records"

    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    downloaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    model = relationship("Model", backref="download_records")


class Favorite(Base):
    """A user favorite relationship for a model."""

    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (UniqueConstraint("model_id", "user_id", name="uix_model_user"),)

    model = relationship("Model", backref="favorites")
