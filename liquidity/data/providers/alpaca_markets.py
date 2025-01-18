from datetime import datetime
from typing import Optional, cast

import pandas as pd
from alpaca.data import CryptoBarsRequest, CryptoHistoricalDataClient, TimeFrame
from dateutil.relativedelta import relativedelta

from liquidity.data.format import formatter_factory
from liquidity.data.metadata.fields import OHLCV, Fields
from liquidity.data.providers.base import DataProviderBase


class AlpacaCryptoDataProvider(DataProviderBase):
    """
    A data provider class to fetch and format cryptocurrency price data
    using Alpaca's CryptoHistoricalDataClient.
    """

    def __init__(self):
        self.client = CryptoHistoricalDataClient()

    def get_prices(
        self,
        ticker: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Fetch and format historical price data for a given cryptocurrency ticker.

        Args:
            ticker (str): The cryptocurrency ticker (e.g., "BTC/USD").
            start (Optional[datetime]): The start date for the data.
                Defaults to one year ago.
            end (Optional[datetime]): The end date for the data.
                Defaults to None (up to the latest available data).

        Returns:
            pd.DataFrame: A DataFrame containing the formatted price data, with the
            index as timestamps and columns named after OHLCV fields.
        """
        df = self._get_raw_data(
            ticker=f"{ticker}/USD",
            start=start or datetime.now() - relativedelta(years=5),
            end=end,
        )
        return self._format_dataframe(df)

    def _get_raw_data(
        self,
        ticker: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Fetch raw historical price data for a cryptocurrency ticker.

        Args:
            ticker (str): The cryptocurrency ticker (e.g., "BTC/USD").


        Returns:
            pd.DataFrame: A DataFrame containing the raw price data.
        """
        request_params = CryptoBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=TimeFrame.Day,
            start=start,
            end=end,
        )
        return self.client.get_crypto_bars(request_params).df

    def _format_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Format the raw dataframe using the common project format.

        Args:
            df (pd.DataFrame): The raw DataFrame fetched from the Alpaca API.

        Returns:
            pd.DataFrame: The formatted DataFrame.
        """
        df.index = cast(
            pd.DatetimeIndex, df.index.get_level_values("timestamp")
        ).tz_localize(None)

        alpaca_formatter = formatter_factory(
            index_name=Fields.Date.value,
            cols_mapper={val.lower(): val for val in OHLCV.all_values()},
            cols_out=OHLCV.all_values(),
        )
        return alpaca_formatter(df)

    def get_dividends(self, ticker: str) -> pd.DataFrame:
        raise RuntimeError("Not available for Crypto")

    def get_treasury_yield(self, maturity: Optional[str]) -> pd.DataFrame:
        raise RuntimeError("Not available for Crypto")
