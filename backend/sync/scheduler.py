"""Scheduler configuration for MakerWorld sync jobs."""
from __future__ import annotations

import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .tasks import sync_models

LOGGER = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone="UTC")
    return _scheduler


def schedule_model_sync(interval_minutes: int = 60) -> None:
    """Schedule the periodic model synchronization job."""

    scheduler = get_scheduler()
    trigger = IntervalTrigger(minutes=interval_minutes)
    scheduler.add_job(
        sync_models,
        trigger=trigger,
        id="makerworld_sync_models",
        replace_existing=True,
        max_instances=1,
    )
    LOGGER.info("Scheduled model sync every %s minutes", interval_minutes)


def start_scheduler() -> None:
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        LOGGER.info("MakerWorld sync scheduler started")


def shutdown_scheduler() -> None:
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        LOGGER.info("MakerWorld sync scheduler stopped")
