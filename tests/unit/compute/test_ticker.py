from unittest.mock import Mock, patch

import pandas as pd
import pytest

from liquidity.compute.ticker import Ticker


@pytest.fixture
def price_data():
    return pd.DataFrame(
        {"Price": [100, 101, 102]}, index=pd.date_range("2025-01-01", periods=3)
    )


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
def ticker_name():
    return "HYG"


@pytest.fixture
def mock_provider(price_data, dividend_data, treasury_yield_data):
    mock = Mock()
    mock.get_prices.return_value = price_data
    mock.get_dividends.return_value = dividend_data
    mock.get_treasury_yield.return_value = treasury_yield_data
    return mock


@pytest.fixture
def mock_metadata(ticker_name):
    return Mock(
        ticker=ticker_name,
        name="Asset name",
        is_treasury_yield=False,
        distribution_frequency=12,
    )


@pytest.fixture
def mock_cache():
    return {}


@pytest.fixture
def ticker(ticker_name, mock_metadata, mock_provider, mock_cache):
    return Ticker(
        name=ticker_name,
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
def compute_yield_mock(compute_dividend_mock):
    with patch("liquidity.compute.ticker.compute_dividend_yield") as m:
        yield m


class TestTicker:
    def test_prices_property(self, ticker, mock_provider):
        _ = ticker._get(ticker._get_key("prices"), ticker._fetch_prices)
        mock_provider.get_prices.assert_called_once_with(ticker.name)

    def test_dividends_property(
        self, ticker, dividend_data, mock_metadata, compute_dividend_mock
    ):
        _ = ticker._get(ticker._get_key("dividends"), ticker._fetch_dividends)
        compute_dividend_mock.assert_called_once_with(
            dividend_data, mock_metadata.distribution_frequency
        )

    def test_yields_property_for_treasury(
        self, ticker, mock_provider, mock_metadata, price_data, dividend_data
    ):
        mock_metadata.is_treasury_yield = True
        mock_metadata.maturity = "10year"
        _ = ticker._get(ticker._get_key("yields"), ticker._fetch_yields)
        mock_provider.get_treasury_yield.assert_called_once_with(mock_metadata.maturity)

    def test_yields_property_for_non_treasury(
        self, ticker, compute_yield_mock, mock_metadata, price_data, dividend_data
    ):
        mock_metadata.is_treasury_yield = False
        _ = ticker._get(ticker._get_key("yields"), ticker._fetch_yields)
        compute_yield_mock.assert_called_once_with(price_data, dividend_data)

    def test_get_key_method(self, ticker):
        assert ticker._get_key("prices") == "HYG-prices"

    def test_get_method_cache_miss(self, ticker, mock_provider):
        cache_key = ticker._get_key("prices")
        ticker._get(cache_key, ticker._fetch_prices)
        mock_provider.get_prices.assert_called_once()

    def test_get_method_cache_hit(self, ticker, mock_provider):
        cache_key = ticker._get_key("prices")
        ticker.cache[cache_key] = pd.DataFrame(
            {"Price": [100, 101, 102]}, index=pd.date_range("2025-01-01", periods=3)
        )
        ticker._get(cache_key, ticker._fetch_prices)
        mock_provider.get_prices.assert_not_called()
