from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from liquidity.data.providers.alpaca_markets import AlpacaCryptoDataProvider


@pytest.fixture
def mock_alpaca_client(sample_raw_data):
    with patch(
        "liquidity.data.providers.alpaca_markets.CryptoHistoricalDataClient"
    ) as mock_client:
        mock_client.return_value.get_crypto_bars.return_value = MagicMock(df=sample_raw_data)

        # Yield the mock client instance
        yield mock_client.return_value


@pytest.fixture
def sample_raw_data():
    index = pd.MultiIndex.from_tuples(
        [
            ("BTC/USD", pd.to_datetime("2023-01-01T06:00:00Z")),
            ("BTC/USD", pd.to_datetime("2023-01-02T06:00:00Z")),
        ],
        names=["symbol", "timestamp"],
    )
    return pd.DataFrame(
        {
            "open": [100, 105],
            "high": [110, 115],
            "low": [90, 95],
            "close": [105, 110],
            "volume": [1000, 1200],
        },
        index=index,
    )


def test_get_prices(mock_alpaca_client):
    provider = AlpacaCryptoDataProvider()
    df = provider.get_prices("BTC/USD")

    mock_alpaca_client.get_crypto_bars.assert_called_once()
    assert df.shape == (2, 5)
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.name == "Date"


def test_get_prices_with_dates(mock_alpaca_client):
    provider = AlpacaCryptoDataProvider()
    start_date, end_date = datetime(2023, 1, 1), datetime(2023, 2, 1)
    df = provider.get_prices("BTC/USD", start=start_date, end=end_date)

    request_params = mock_alpaca_client.get_crypto_bars.call_args[0][0]

    # validate call parameters
    assert request_params.start == start_date
    assert request_params.end == end_date

    # validate result
    assert df.shape == (2, 5)
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.name == "Date"


def test_get_dividends_raises():
    provider = AlpacaCryptoDataProvider()
    with pytest.raises(RuntimeError, match="Not available for Crypto"):
        provider.get_dividends("BTC/USD")


def test_get_treasury_yield_raises():
    provider = AlpacaCryptoDataProvider()
    with pytest.raises(RuntimeError, match="Not available for Crypto"):
        provider.get_treasury_yield("10Y")
