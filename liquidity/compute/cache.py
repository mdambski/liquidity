import functools
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Union

import pandas as pd
from pydantic import Field
from pydantic_settings import BaseSettings

from liquidity.data.metadata.fields import Fields


class CacheConfig(BaseSettings):
    """Configuration settings for Alpha Vantage API."""

    enabled: bool = Field(default=True, alias="CACHE_ENABLED")
    data_dir: Path = Field(
        default=Path.home() / ".liquidity" / "data",
        alias="CACHE_DATA_DIR",
    )

    @classmethod
    def cache_dir(cls) -> Path:
        """Return the cache directory for the current date."""
        path = cls().data_dir / datetime.now().strftime("%Y%m%d")
        path.mkdir(parents=True, exist_ok=True)
        return path


def generate_cache_key(func, args, kwargs):
    """Generate a unique cache key based on function name and arguments."""
    key = "-".join([func.__name__, *args, *kwargs])
    return hashlib.blake2b(key.encode()).hexdigest()


def cache_with_persistence(func):
    """Decorator to cache function outputs in-memory and persist to disk."""
    cache, cache_dir = {}, CacheConfig.cache_dir()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = generate_cache_key(func, args[1:], kwargs)

        if key in cache:
            return cache[key]

        file_path = cache_dir / f"{key}.csv"
        if file_path.exists():
            df = pd.read_csv(
                file_path, index_col=Fields.Date.value, parse_dates=[Fields.Date.value]
            )
            cache[key] = df
            return cache[key]

        result = func(*args, **kwargs)
        cache[key] = result
        result.to_csv(file_path)
        return result

    return wrapper


class InMemoryCacheWithPersistence(dict):
    """In-memory cache with file system persistence.

    Holds data in-memory but saves it locally, in order to retrieve
    data between executions. This can lower number of api calls.
    """

    def __init__(self, cache_dir: Union[str, Path]):
        super().__init__()
        self.cache_dir = os.path.join(cache_dir, self.get_date())
        self.ensure_cache_dir()

    def get_date(self) -> str:
        formatted_date = datetime.now().strftime("%Y%m%d")
        return formatted_date

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
