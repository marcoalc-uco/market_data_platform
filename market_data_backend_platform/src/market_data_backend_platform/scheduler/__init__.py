"""Scheduler for automated data ingestion.

This module configures APScheduler to run periodic ingestion tasks.
The scheduler integrates with FastAPI lifecycle events.

Example::

    from fastapi import FastAPI
    from market_data_backend_platform.scheduler import start_scheduler, shutdown_scheduler

    app = FastAPI()

    @app.on_event("startup")
    async def startup():
        start_scheduler()

    @app.on_event("shutdown")
    async def shutdown():
        shutdown_scheduler()
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from market_data_backend_platform.core import get_logger
from market_data_backend_platform.core.config import settings
from market_data_backend_platform.db.session import SessionLocal
from market_data_backend_platform.etl.clients.yahoo import YahooFinanceClient
from market_data_backend_platform.etl.services.ingestion import IngestionService
from market_data_backend_platform.repositories.instrument import (
    InstrumentRepository,
)
from market_data_backend_platform.repositories.market_price import (
    MarketPriceRepository,
)

logger = get_logger(__name__)

# Global scheduler instance
_scheduler: BackgroundScheduler | None = None


def run_ingestion_job() -> None:
    """Execute the ingestion job.

    Creates a new database session, runs ingestion for all active
    instruments, then closes the session.
    """
    logger.info("scheduler_job_started")

    session = SessionLocal()
    try:
        service = IngestionService(
            instrument_repo=InstrumentRepository(session),
            price_repo=MarketPriceRepository(session),
            yahoo_client=YahooFinanceClient(),
        )

        result = service.ingest_all_active(
            interval="5m",
            period="1d",  # Intraday 5-min bars for today
        )

        logger.info(
            "scheduler_job_complete",
            total_instruments=result["total_instruments"],
            total_inserted=result["total_inserted"],
            failed=result["failed"],
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("scheduler_job_failed", error=str(exc))
    finally:
        session.close()


def start_scheduler(interval_minutes: int | None = None) -> None:
    """Start the background scheduler.

    Args:
        interval_minutes: Minutes between ingestion runs.
            Defaults to settings.INGESTION_INTERVAL_MINUTES.
    """
    global _scheduler  # pylint: disable=global-statement

    if _scheduler is not None:
        logger.warning("scheduler_already_running")
        return

    interval = interval_minutes or getattr(settings, "ingestion_interval_minutes", 60)

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        run_ingestion_job,
        trigger=IntervalTrigger(minutes=interval),
        id="ingestion_job",
        name="Market Data Ingestion",
        replace_existing=True,
    )
    _scheduler.start()

    logger.info(
        "scheduler_started",
        interval_minutes=interval,
    )


def shutdown_scheduler() -> None:
    """Shutdown the scheduler gracefully."""
    global _scheduler  # pylint: disable=global-statement

    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("scheduler_stopped")
