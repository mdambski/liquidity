from __future__ import annotations

from typing import Optional

import pandas as pd
from alpha_vantage.econindicators import EconIndicators
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.timeseries import TimeSeries
from pydantic import Field
from pydantic_settings import BaseSettings

from liquidity.data.format import formatter_factory
from liquidity.data.metadata.fields import OHLCV, Fields
from liquidity.data.providers.base import DataProviderBase


class AlphaVantageConfig(BaseSettings):
    """Configuration settings for Alpha Vantage API."""

    api_key: Optional[str] = Field(default=None, alias="ALPHAVANTAGE_API_KEY")


class AlphaVantageDataProvider(DataProviderBase):
    """Data provider class to fetch financial data from Alpha Vantage API."""

    name = "av"

    def __init__(self, api_key: str = None) -> None:
        self.api_key = api_key or AlphaVantageConfig().api_key
        self.output_format = "pandas"

    def get_prices(self, ticker, output_size: str = "full") -> pd.DataFrame:
        """
        Fetches daily price data for a given ticker symbol.

        Args:
            ticker (str): The stock symbol (ticker) for which to retrieve price data.
            output_size (str, optional): The size of the call, supported values are
                'compact' and 'full; the first returns the last 100 points in the
                data series, and 'full' returns the full-length daily times
                series, commonly above 1MB. Default is "full".

        Returns:
            pd.DataFrame: A DataFrame containing the formatted OHLCV price data.
        """
        client = TimeSeries(key=self.api_key, output_format="pandas")
        df, _ = client.get_daily(ticker, outputsize=output_size)
        av_prices_formatter = formatter_factory(
            cols_mapper={
                "1. open": OHLCV.Open.value,
                "2. high": OHLCV.High.value,
                "3. low": OHLCV.Low.value,
                "4. close": OHLCV.Close.value,
                "5. volume": OHLCV.Volume.value,
            },
        )
        return av_prices_formatter(df)

    def get_dividends(self, ticker: str) -> pd.DataFrame:
        """
        Fetches dividend data for a given ticker symbol.

        Args:
            ticker (str): The stock symbol (ticker) for which to retrieve dividend data.

        Returns:
            pd.DataFrame: A DataFrame containing the formatted dividend data.
        """
        client = FundamentalData(key=self.api_key, output_format="pandas")
        df, _ = client.get_dividends(ticker)
        av_dividend_formatter = formatter_factory(
            cols_mapper={
                "amount": Fields.Dividends.value,
                "ex_dividend_date": Fields.Date.value,
            },
            index_col=Fields.Date.value,
            cols_out=[Fields.Dividends.value],
            to_numeric=[Fields.Dividends.value],
        )
        return av_dividend_formatter(df)

    def get_treasury_yield(self, maturity: str = '10year') -> pd.DataFrame:
        """
        Fetches treasury yield data for a specified maturity period.

        Args:
            maturity (str): The maturity period for the treasury yield.
                Supported values are '3month', '2year', '5year', '7year',
                '10year', '30year' (default '10year').

        Returns:
            pd.DataFrame: A DataFrame containing the formatted treasury yield data.
        """
        client = EconIndicators(self.api_key, output_format="pandas")
        df, _ = client.get_treasury_yield(maturity=maturity)
        av_treasury_yield_formatter = formatter_factory(
            cols_mapper={"date": Fields.Date.value, "value": Fields.Yield.value},
            index_col=Fields.Date.value,
            cols_out=[Fields.Yield.value],
            to_numeric=[Fields.Yield.value],
        )
        return av_treasury_yield_formatter(df)
