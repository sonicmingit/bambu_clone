"""Application database models."""
from .base import Base
from .model import Model, ModelStats
from .records import DownloadRecord, Favorite

__all__ = [
    "Base",
    "Model",
    "ModelStats",
    "DownloadRecord",
    "Favorite",
]
