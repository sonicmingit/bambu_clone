"""SQLAlchemy models representing downloadable ML models."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from .base import Base


class Model(Base):
    """A machine learning model that can be downloaded by users."""

    __tablename__ = "models"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    checksum = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ModelStats(Base):
    """Aggregated statistics for downloads and favorites."""

    __tablename__ = "model_stats"

    model_id = Column(Integer, primary_key=True)
    downloads = Column(Integer, default=0, nullable=False)
    favorites = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
