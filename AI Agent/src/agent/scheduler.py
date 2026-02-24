from __future__ import annotations

import logging
import signal
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import load_settings
from .main import run_once


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_scheduler() -> None:
    settings = load_settings()

    scheduler = BackgroundScheduler(timezone=settings.timezone)
    scheduler.add_job(
        run_once,
        CronTrigger(hour=settings.schedule_hour, minute=settings.schedule_minute),
        id="daily_outfit_email",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler started. Send at %02d:%02d (%s).",
        settings.schedule_hour,
        settings.schedule_minute,
        settings.timezone,
    )

    should_run = True

    def _stop(_sig, _frame) -> None:  # type: ignore[no-untyped-def]
        nonlocal should_run
        should_run = False

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    try:
        while should_run:
            time.sleep(1)
    finally:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    run_scheduler()
