import urllib.parse
from datetime import datetime

import pandas as pd
import pytest
import responses
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from pandas import testing as pdt

from liquidity.data.metadata.fields import OHLCV
from liquidity.data.providers.alpaca_markets import AlpacaCryptoDataProvider


class TestAlpacaCryptoDataProvider:
    @pytest.fixture
    def ticker(self):
        return "ETH/USD"

    @pytest.fixture
    def api_response_json(self, ticker):
        return {
            "bars": {
                ticker: [
                    {
                        "c": 2380.1305,
                        "h": 2403,
                        "l": 2274.13,
                        "n": 142,
                        "o": 2274.9615,
                        "t": "2024-01-01T06:00:00Z",
                        "v": 176.411074325,
                        "vw": 2384.4248295578,
                    },
                    {
                        "c": 2378.65,
                        "h": 2433.165,
                        "l": 2346.87,
                        "n": 157,
                        "o": 2380.4135,
                        "t": "2024-01-02T06:00:00Z",
                        "v": 22.437474624,
                        "vw": 2373.0654174505,
                    },
                ]
            },
            "next_page_token": None,
        }

    @pytest.fixture
    def api_url(self, ticker):
        url = "https://data.alpaca.markets/v1beta3/crypto/us/bars"
        params = CryptoBarsRequest(
            symbol_or_symbols=f"{ticker}/USD",
            timeframe=TimeFrame.Day,
            start=datetime(2024, 1, 1),
        )
        return "?".join([url, urllib.parse.urlencode(params.to_request_fields())])

    @pytest.fixture
    def data_provider(self):
        return AlpacaCryptoDataProvider()

    @responses.activate
    def test_get_prices(self, data_provider, ticker, api_url, api_response_json):
        responses.add(responses.GET, api_url, json=api_response_json, status=200)

        df = data_provider.get_prices(ticker, start=datetime(2024, 1, 1))

        # Assert DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == list(OHLCV)
        assert isinstance(df.index, pd.DatetimeIndex)

        # Check if selected fields match and have correct format
        expected_df = pd.DataFrame(
            data={
                "Open": [2274.9615, 2380.4135],
                "High": [2403, 2433.165],
                "Low": [2274.13, 2346.87],
                "Close": [2380.1305, 2378.65],
                "Volume": [176.411074325, 22.437474624],
            },
            index=pd.DatetimeIndex(
                data=pd.to_datetime(["2024-01-01T06:00:00", "2024-01-02T06:00:00"]),
                name="Date",
            ),
        )

        pdt.assert_frame_equal(df, expected_df)
