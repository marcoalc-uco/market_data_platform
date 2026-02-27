"""ETL module for data ingestion from external sources.

This module provides:
- API clients for external data sources (Yahoo Finance)
- Data transformers to normalize responses
- Ingestion services to load data into the database
"""

from market_data_backend_platform.etl.clients import YahooFinanceClient
from market_data_backend_platform.etl.services import IngestionService

__all__ = [
    "YahooFinanceClient",
    "IngestionService",
]
