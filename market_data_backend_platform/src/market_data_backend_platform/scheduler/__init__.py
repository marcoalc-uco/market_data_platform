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
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from market_data_backend_platform.core import get_logger
from market_data_backend_platform.core.config import settings
from market_data_backend_platform.db.session import SessionLocal
from market_data_backend_platform.etl.clients.yahoo import YahooFinanceClient
from market_data_backend_platform.etl.services.ingestion import IngestionService
from market_data_backend_platform.models.instrument import InstrumentType
from market_data_backend_platform.repositories.instrument import (
    InstrumentRepository,
)
from market_data_backend_platform.repositories.market_price import (
    MarketPriceRepository,
)

logger = get_logger(__name__)

# Global scheduler instance
_scheduler: BackgroundScheduler | None = None


# Instrument types that support intraday data (5m candles from Yahoo Finance)
_INTRADAY_TYPES = [InstrumentType.STOCK, InstrumentType.CRYPTO]

# Instrument types that only support daily data (no intraday quotes available)
_DAILY_ONLY_TYPES = [InstrumentType.INDEX]


def _build_service(session: object) -> IngestionService:
    return IngestionService(
        instrument_repo=InstrumentRepository(session),  # type: ignore[arg-type]
        price_repo=MarketPriceRepository(session),  # type: ignore[arg-type]
        yahoo_client=YahooFinanceClient(),
    )


def run_intraday_job() -> None:
    """Ingest intraday data (5m candles) for STOCK and CRYPTO instruments."""
    logger.info("scheduler_intraday_job_started")
    session = SessionLocal()
    try:
        result = _build_service(session).ingest_all_active(
            interval="5m",
            period="1d",
            instrument_types=_INTRADAY_TYPES,
        )
        logger.info("scheduler_intraday_job_complete", **result)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("scheduler_intraday_job_failed", error=str(exc))
    finally:
        session.close()


def run_daily_job() -> None:
    """Ingest daily data (1d candles) for INDEX instruments.

    INDEX instruments (e.g. mutual funds, index funds) do not publish
    intraday quotes on Yahoo Finance — requesting a 5m interval returns
    an error. This job runs once per day after market close.
    """
    logger.info("scheduler_daily_job_started")
    session = SessionLocal()
    try:
        result = _build_service(session).ingest_all_active(
            interval="1d",
            period="1y",
            instrument_types=_DAILY_ONLY_TYPES,
        )
        logger.info("scheduler_daily_job_complete", **result)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("scheduler_daily_job_failed", error=str(exc))
    finally:
        session.close()


def start_scheduler(interval_minutes: int | None = None) -> None:
    """Start the background scheduler with two jobs:

    - Intraday job: fetches 5m candles for STOCK/CRYPTO every N minutes.
    - Daily job: fetches 1d candles for INDEX instruments once per day at 18:30.

    Args:
        interval_minutes: Minutes between intraday runs.
            Defaults to settings.ingestion_interval_minutes.
    """
    global _scheduler  # pylint: disable=global-statement

    if _scheduler is not None:
        logger.warning("scheduler_already_running")
        return

    interval = interval_minutes or getattr(settings, "ingestion_interval_minutes", 60)

    _scheduler = BackgroundScheduler()

    # Intraday job — STOCK and CRYPTO (supports 5m candles)
    _scheduler.add_job(
        run_intraday_job,
        trigger=IntervalTrigger(minutes=interval),
        id="intraday_ingestion_job",
        name="Intraday Market Data Ingestion (STOCK, CRYPTO)",
        replace_existing=True,
    )

    # Daily job — INDEX instruments (no intraday data available on Yahoo Finance)
    # Runs at 17:30 Europe/Madrid (handles DST automatically: UTC+1 winter, UTC+2 summer)
    _scheduler.add_job(
        run_daily_job,
        trigger=CronTrigger(hour=18, minute=00, timezone="Europe/Madrid"),
        id="daily_ingestion_job",
        name="Daily Market Data Ingestion (INDEX)",
        replace_existing=True,
    )

    _scheduler.start()

    logger.info(
        "scheduler_started",
        intraday_interval_minutes=interval,
        daily_job_time="17:30 Europe/Madrid",
    )


def shutdown_scheduler() -> None:
    """Shutdown the scheduler gracefully."""
    global _scheduler  # pylint: disable=global-statement

    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("scheduler_stopped")
