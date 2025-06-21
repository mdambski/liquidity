from unittest.mock import Mock, patch

import pandas as pd
import pytest

from liquidity.compute.ticker import Ticker


@pytest.fixture
def price_data():
    return pd.DataFrame({"Price": [100, 101, 102]}, index=pd.date_range("2025-01-01", periods=3))


@pytest.fixture
def dividend_data():
    return pd.DataFrame(
        {"Dividends": [0.5, 0.6, 0.7]}, index=pd.date_range("2025-01-01", periods=3)
    )


@pytest.fixture
def treasury_yield_data():
    return pd.DataFrame(
        {"Yield": [0.02, 0.021, 0.022]}, index=pd.date_range("2025-01-01", periods=3)
    )


@pytest.fixture
def yield_data():
    return pd.DataFrame({"Yield": [0.2, 0.3, 0.4]}, index=pd.date_range("2024-01-01", periods=3))


@pytest.fixture
def ticker_symbol():
    return "HYG"


@pytest.fixture
def mock_provider(price_data, dividend_data, treasury_yield_data):
    mock = Mock()
    mock.get_prices.return_value = price_data
    mock.get_dividends.return_value = dividend_data
    mock.get_treasury_yield.return_value = treasury_yield_data
    return mock


@pytest.fixture
def mock_metadata(ticker_symbol):
    return Mock(
        ticker=ticker_symbol,
        name="Asset name",
        is_treasury_yield=False,
        distribution_frequency=12,
    )


@pytest.fixture
def mock_cache():
    return {}


@pytest.fixture
def ticker(ticker_symbol, mock_metadata, mock_provider, mock_cache):
    return Ticker(
        symbol=ticker_symbol,
        metadata=mock_metadata,
        provider=mock_provider,
        cache=mock_cache,
    )


@pytest.fixture
def compute_dividend_mock(dividend_data):
    with patch("liquidity.compute.ticker.compute_ttm_dividend") as m:
        m.return_value = dividend_data
        yield m


@pytest.fixture
def compute_yield_mock(compute_dividend_mock, yield_data):
    with patch("liquidity.compute.ticker.compute_dividend_yield") as m:
        m.return_value = yield_data
        yield m


class TestTicker:
    def test_prices_property(self, ticker, mock_provider, price_data):
        df = ticker.prices

        mock_provider.get_prices.assert_called_once_with(ticker.symbol)
        pd.testing.assert_frame_equal(df, price_data)

    def test_dividends_property(self, ticker, dividend_data, mock_metadata, compute_dividend_mock):
        df = ticker.dividends

        compute_dividend_mock.assert_called_once_with(
            dividend_data, mock_metadata.distribution_frequency
        )
        pd.testing.assert_frame_equal(df, dividend_data)

    def test_yields_property_for_treasury(
        self,
        ticker,
        mock_provider,
        mock_metadata,
        price_data,
        dividend_data,
        treasury_yield_data,
    ):
        mock_metadata.is_treasury_yield = True
        mock_metadata.maturity = "10year"

        df = ticker.yields

        mock_provider.get_treasury_yield.assert_called_once_with(mock_metadata.maturity)
        pd.testing.assert_frame_equal(df, treasury_yield_data)

    def test_yields_property_for_non_treasury(
        self,
        ticker,
        compute_yield_mock,
        mock_metadata,
        price_data,
        dividend_data,
        yield_data,
    ):
        mock_metadata.is_treasury_yield = False

        df = ticker.yields

        compute_yield_mock.assert_called_once_with(price_data, dividend_data)
        pd.testing.assert_frame_equal(df, yield_data)

    def test_get_key_method(self, ticker):
        assert ticker._get_key("prices") == "HYG-prices"

    def test_get_method_cache_miss(self, ticker, mock_provider):
        _ = ticker.prices
        mock_provider.get_prices.assert_called_once()

    def test_get_method_cache_hit(self, ticker, mock_provider):
        cache_key = ticker._get_key("prices")
        ticker.cache[cache_key] = pd.DataFrame(
            {"Price": [100, 101, 102]}, index=pd.date_range("2025-01-01", periods=3)
        )
        _ = ticker.prices
        mock_provider.get_prices.assert_not_called()
