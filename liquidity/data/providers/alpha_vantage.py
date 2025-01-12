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
    api_key: Optional[str] = Field(default=None, alias="ALPHAVANTAGE_API_KEY")


class AlphaVantageDataProvider(DataProviderBase):
    name = "av"

    def __init__(self, api_key: str = None) -> None:
        self.api_key = api_key or AlphaVantageConfig().api_key
        self.output_format = "pandas"

    def get_prices(self, ticker, output_size: str = "full") -> pd.DataFrame:
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
        client = FundamentalData(key=self.api_key, output_format="pandas")
        df, _ = client.get_dividends(ticker)
        av_dividend_formatter = formatter_factory(
            cols_mapper={"amount": Fields.Dividends, "ex_dividend_date": Fields.Date},
            index_col=Fields.Date,
            cols_out=[Fields.Dividends],
            to_numeric=[Fields.Dividends],
        )
        return av_dividend_formatter(df)

    def get_treasury_yield(self, maturity: str) -> pd.DataFrame:
        client = EconIndicators(self.api_key, output_format="pandas")
        df, _ = client.get_treasury_yield(maturity=maturity)
        av_treasury_yield_formatter = formatter_factory(
            cols_mapper={"date": Fields.Date, "value": Fields.Yield},
            index_col=Fields.Date,
            cols_out=[Fields.Yield],
            to_numeric=[Fields.Yield],
        )
        return av_treasury_yield_formatter(df)
