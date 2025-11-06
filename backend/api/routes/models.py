"""API routes for model statistics and actions."""
from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...database import get_session
from ...models import DownloadRecord, Favorite, ModelStats

router = APIRouter(prefix="/models", tags=["models"])


class StatsUpdateRequest(BaseModel):
    """Request body for updating model statistics."""

    action: Literal["download", "favorite", "unfavorite"] = Field(..., description="Type of action performed")
    model_id: int = Field(..., description="Model identifier")
    user_id: Optional[int] = Field(None, description="Optional user identifier")
    ip_address: Optional[str] = Field(None, description="IP address for download tracking")
    user_agent: Optional[str] = Field(None, description="User agent for download tracking")


class StatsResponse(BaseModel):
    """Response body with aggregated model statistics."""

    model_id: int
    downloads: int
    favorites: int
    is_favorite: Optional[bool] = Field(None, description="Whether the requesting user has favorited the model")


def _get_or_create_stats(session: Session, model_id: int) -> ModelStats:
    stats = session.get(ModelStats, model_id)
    if stats is None:
        stats = ModelStats(model_id=model_id)
        session.add(stats)
        session.flush()
    return stats


@router.get("/{model_id}/stats", response_model=StatsResponse)
def get_model_stats(
    model_id: int,
    user_id: Optional[int] = None,
    session: Session = Depends(get_session),
) -> StatsResponse:
    """Retrieve aggregated statistics for a model."""

    stats = _get_or_create_stats(session, model_id)
    is_favorite = None
    if user_id is not None:
        favorite_query = select(Favorite).where(Favorite.model_id == model_id, Favorite.user_id == user_id)
        is_favorite = session.execute(favorite_query).scalar_one_or_none() is not None
    session.commit()
    return StatsResponse(
        model_id=stats.model_id,
        downloads=stats.downloads,
        favorites=stats.favorites,
        is_favorite=is_favorite,
    )


@router.post("/stats", response_model=StatsResponse, status_code=status.HTTP_200_OK)
def update_model_stats(
    payload: StatsUpdateRequest,
    session: Session = Depends(get_session),
) -> StatsResponse:
    """Update aggregated statistics based on a model action."""

    stats = _get_or_create_stats(session, payload.model_id)
    is_favorite: Optional[bool] = None

    if payload.action == "download":
        record = DownloadRecord(
            model_id=payload.model_id,
            user_id=payload.user_id,
            ip_address=payload.ip_address,
            user_agent=payload.user_agent,
        )
        session.add(record)
        stats.downloads += 1
    elif payload.action == "favorite":
        if payload.user_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id is required for favorite")
        favorite = Favorite(model_id=payload.model_id, user_id=payload.user_id)
        session.add(favorite)
        try:
            session.flush()
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Favorite already exists for this user.",
            ) from exc
        stats.favorites += 1
        is_favorite = True
    elif payload.action == "unfavorite":
        if payload.user_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id is required for unfavorite")
        favorite_query = select(Favorite).where(
            Favorite.model_id == payload.model_id, Favorite.user_id == payload.user_id
        )
        favorite = session.execute(favorite_query).scalar_one_or_none()
        if favorite is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found.")
        session.delete(favorite)
        stats.favorites = max(0, stats.favorites - 1)
        is_favorite = False
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported action")

    session.commit()

    if is_favorite is None and payload.user_id is not None:
        favorite_query = select(Favorite).where(
            Favorite.model_id == payload.model_id, Favorite.user_id == payload.user_id
        )
        is_favorite = session.execute(favorite_query).scalar_one_or_none() is not None

    return StatsResponse(
        model_id=stats.model_id,
        downloads=stats.downloads,
        favorites=stats.favorites,
        is_favorite=is_favorite,
    )
