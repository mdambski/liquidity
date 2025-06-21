from typing import Optional

import pandas as pd
from fredapi import Fred  # type: ignore
from pydantic import Field
from pydantic_settings import BaseSettings

from liquidity.compute.cache import cache_with_persistence


class FredConfig(BaseSettings):
    """Configuration settings for FRED Economic data API."""

    api_key: Optional[str] = Field(default=None, alias="FRED_API_KEY")


class FredEconomicDataProvider:
    def __init__(self, api_key: Optional[str] = None):
        self.client = Fred(api_key=api_key or FredConfig().api_key)

    @cache_with_persistence
    def get_data(self, ticker: str) -> pd.DataFrame:
        data = self.client.get_series(ticker)
        df = pd.DataFrame(data, columns=["Close"])
        df.index.name = "Date"
        return df
