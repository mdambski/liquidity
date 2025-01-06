import os

import logging
from os.path import expanduser

import pandas as pd

from liquidity.compute.utils import dividends, yields
from liquidity.data.config import get_data_provider
from liquidity.data.format import format_as_yield
from liquidity.data.metadata.assets import get_asset_catalog, get_ticker_metadata
from liquidity.data.metadata.entities import AssetMetadata, AssetTypes

from liquidity.exceptions import DataNotAvailable

from liquidity.data.providers.base import DataProviderBase
from liquidity.data.providers.alpha_vantage import AlphaVantageDataProvider
from liquidity.data.providers.local import LocalStorageDataProvider
from liquidity.compute.utils.dividends import compute_ttm_dividend
from liquidity.compute.utils.yields import compute_dividend_yield

logger = logging.getLogger(__name__)


CACHE_DIR = os.path.join(expanduser("~"), ".liquidity")
CACHE_DATA_DIR = os.path.join(CACHE_DIR, "data")


class InMemoryCacheWithPersistence(dict):
    """In-memory cache with file system persistence.

    Holds data in-memory but saves it locally, in order to retrieve
    data between executions. This can lower number of api calls.
    """

    def __init__(self, cache_dir: str = CACHE_DATA_DIR):
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
        file = os.path.join(self.cache_dir, f"{key}.csv")
        if os.path.exists(file):
            super().__setitem__(key, pd.read_csv(file))
        return super().__getitem__(key)


class Ticker:
    def __init__(self, name: str):
        self.name = name
        self.metadata = get_ticker_metadata(name)
        self.provider = get_data_provider(name)
        self.cache = InMemoryCacheWithPersistence()

    def get_key(self, data_type: str) -> str:
        """Returns key for the cache storage and retrieval."""
        return f"{self.name}-{data_type}"

    @property
    def prices(self) -> pd.DataFrame:
        key = self.get_key("prices")
        if key not in self.cache:
            self.cache[key] = self.provider.get_prices(self.name)
        return self.cache[key]

    @property
    def dividends(self) -> pd.DataFrame:
        key = self.get_key("dividends")
        if key not in self.cache:
            df = self.provider.get_dividends(self.name)
            self.cache[key] = dividends.compute_ttm_dividend(df)
        return self.cache[key]

    @property
    def yields(self) -> pd.DataFrame:
        key = self.get_key("yields")
        if key not in self.cache:
            if self.metadata.is_yield:
                self.cache[key] = format_as_yield(self.prices)
            else:
                self.cache[key] = yields.compute_dividend_yield(
                    self.prices, self.dividends
                )
        return self.cache[key]
