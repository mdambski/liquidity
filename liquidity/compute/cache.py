import os
from os.path import expanduser

import pandas as pd
from pydantic import Field
from pydantic_settings import BaseSettings

from liquidity.data.metadata.fields import Fields


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


def get_cache() -> dict:
    """Return cache instance"""
    cache_config = CacheConfig()
    if cache_config.enabled:
        return InMemoryCacheWithPersistence(cache_config.data_dir)
    return {}
