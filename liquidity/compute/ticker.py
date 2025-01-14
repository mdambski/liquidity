import logging
import os
from os.path import expanduser

import pandas as pd
from pydantic import Field
from pydantic_settings import BaseSettings

from liquidity.compute.utils import dividends, yields
from liquidity.data.config import get_data_provider
from liquidity.data.metadata.assets import get_ticker_metadata
from liquidity.data.metadata.fields import Fields

logger = logging.getLogger(__name__)


class CacheConfig(BaseSettings):
    """Configuration settings for Alpha Vantage API."""

    enabled: bool = Field(default=True, alias="CACHE_ENABLED")
    data_dir: str = Field(
        default=os.path.join(expanduser("~"), ".liquidity", "data"),
        alias="CACHE_DATA_DIR",
    )


class InMemoryCacheWithPersistence(dict):
    """In-memory cache with file system persistence.

    Holds data in-memory but saves it locally, in order to retrieve
    data between executions. This can lower number of api calls.
    """

    def __init__(self, cache_dir: str):
        super().__init__()
        self.cache_dir = cache_dir
        self.ensure_cache_dir()

    def ensure_cache_dir(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        value.to_csv(os.path.join(self.cache_dir, f"{key}.csv"))

    def __missing__(self, key):
        """Load data from disk if not in memory yet."""
        file_path = os.path.join(self.cache_dir, f"{key}.csv")
        if not os.path.exists(file_path):
            raise KeyError(key)

        idx_name = Fields.Date.value
        value = pd.read_csv(file_path, index_col=idx_name, parse_dates=[idx_name])
        super().__setitem__(key, value)

        return value


class Ticker:
    def __init__(self, name: str):
        self.name = name
        self.metadata = get_ticker_metadata(name)
        self.provider = get_data_provider(name)
        self.cache = self.initialize_cache()

    def initialize_cache(self):
        config = CacheConfig()
        if config.enabled:
            return InMemoryCacheWithPersistence(config.data_dir)
        return {}

    def get_key(self, data_type: str) -> str:
        """Returns key for the cache storage and retrieval."""
        return f"{self.name}-{data_type}"

    @property
    def prices(self) -> pd.DataFrame:
        key = self.get_key("prices")
        try:
            # Attempt to retrieve the key from the cache.
            # If it's not found in memory, the cache will
            # attempt to load it from disk.
            return self.cache[key]
        except KeyError:
            self.cache[key] = self.provider.get_prices(self.name)
        return self.cache[key]

    @property
    def dividends(self) -> pd.DataFrame:
        key = self.get_key("dividends")
        try:
            # Attempt to retrieve the key from the cache.
            # If it's not found in memory, the cache will
            # attempt to load it from disk.
            return self.cache[key]
        except KeyError:
            df = self.provider.get_dividends(self.name)
            self.cache[key] = dividends.compute_ttm_dividend(
                df, self.metadata.distribution_frequency
            )
        return self.cache[key]

    @property
    def yields(self) -> pd.DataFrame:
        key = self.get_key("yields")
        try:
            # Attempt to retrieve the key from the cache.
            # If it's not found in memory, the cache will
            # attempt to load it from disk.
            return self.cache[key]
        except KeyError:
            if self.metadata.is_yield:
                self.cache[key] = self.provider.get_treasury_yield(
                    self.metadata.maturity
                )
            else:
                self.cache[key] = yields.compute_dividend_yield(
                    self.prices, self.dividends
                )
        return self.cache[key]
