import pandas as pd
import pytest

from liquidity.data.providers.alpha_vantage import AlphaVantageDataProvider
from liquidity.data.metadata.fields import OHLCV, Fields


@pytest.fixture
def data_provider():
    provider = AlphaVantageDataProvider()
    if provider.api_key is None:
        raise ValueError(
            "Missing Alpha vantage api key. Make sure "
            "ALPHAVANTAGE_API_KEY env variable is set"
            "in order to run test using real api call."
        )
    yield provider


def test_retrieve_price_data(data_provider):
    df = data_provider.get_prices("LQD")
    assert isinstance(df.index, pd.DatetimeIndex)
    assert set(df.columns) == {
        OHLCV.Open,
        OHLCV.High,
        OHLCV.Low,
        OHLCV.Close,
        OHLCV.Volume,
    }


def test_retrieve_dividend_data(data_provider):
    df = data_provider.get_dividends("LQD")
    assert isinstance(df.index, pd.DatetimeIndex)
    assert set(df.columns) == {Fields.Dividends}
