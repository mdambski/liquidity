from typing import Callable

import pandas as pd

from liquidity.compute.cache import get_cache
from liquidity.compute.utils.dividends import compute_ttm_dividend
from liquidity.compute.utils.yields import compute_dividend_yield
from liquidity.data.config import get_data_provider
from liquidity.data.metadata.assets import get_ticker_metadata
from liquidity.data.metadata.entities import AssetMetadata
from liquidity.data.providers.base import DataProviderBase


class Ticker:
    def __init__(
        self,
        name: str,
        metadata: AssetMetadata,
        provider: DataProviderBase,
        cache: dict,
    ):
        """
        Initialize a Ticker object.

        Args:
            name (str): The ticker symbol.
            metadata (AssetMetadata): Metadata about the asset.
            provider (DataProviderBase): Data provider for retrieving asset data.
            cache (dict): Cache for storing and retrieving data.

        Simpler Initialization:
            Use the `Ticker.for_name(name: str)` class method for easier initialization:

            Example:
                ticker = Ticker.for_name("SPX")
        """
        self.name = name
        self.metadata = metadata
        self.provider = provider
        self.cache = cache

    def _get_key(self, data_type: str) -> str:
        """Returns key for the cache storage and retrieval."""
        return f"{self.name}-{data_type}"

    def _get(
        self, cache_key: str, fetch_fn: Callable[[], pd.DataFrame]
    ) -> pd.DataFrame:
        """Retrieve data from cache or fetch using the provided function."""
        try:
            return self.cache[cache_key]
        except KeyError:
            self.cache[cache_key] = fetch_fn()
            return self.cache[cache_key]

    def _fetch_prices(self) -> pd.DataFrame:
        return self.provider.get_prices(self.name)

    def _fetch_yields(self) -> pd.DataFrame:
        if self.metadata.is_treasury_yield:
            return self.provider.get_treasury_yield(self.metadata.maturity)
        return compute_dividend_yield(self.prices, self.dividends)

    def _fetch_dividends(self) -> pd.DataFrame:
        df = self.provider.get_dividends(self.name)
        return compute_ttm_dividend(df, self.metadata.distribution_frequency)

    @property
    def prices(self) -> pd.DataFrame:
        return self._get(self._get_key("prices"), self._fetch_prices)

    @property
    def dividends(self) -> pd.DataFrame:
        return self._get(self._get_key("dividends"), self._fetch_dividends)

    @property
    def yields(self) -> pd.DataFrame:
        return self._get(self._get_key("yields"), self._fetch_yields)

    @classmethod
    def from_name(cls, name: str) -> "Ticker":
        return cls(
            name=name,
            metadata=get_ticker_metadata(name),
            provider=get_data_provider(name),
            cache=get_cache(),
        )
