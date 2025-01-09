import os

import pytest

from liquidity.data.providers.alpha_vantage import AlphaVantageDataProvider


@pytest.fixture
def api_key():
    return "fake-api-key"


@pytest.fixture
def ticker():
    return "AAPL"


@pytest.fixture
def av_base_api_url(api_key, ticker):
    return "https://www.alphavantage.co/query?"


@pytest.fixture
def av_data_provider(api_key):
    return AlphaVantageDataProvider(api_key)


@pytest.fixture
def fixtures_dir():
    return os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture
def treasury_yield_fixture_path(fixtures_dir):
    return os.path.join(fixtures_dir, "treasury_yield_monthly_10year.json")
