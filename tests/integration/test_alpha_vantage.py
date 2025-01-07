import pandas as pd
import pytest
import urllib.parse
from liquidity.data.providers.alpha_vantage import AlphaVantageDataProvider
from liquidity.data.metadata.fields import OHLCV, Fields
import responses
from pandas import testing as pdt


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
def data_provider(api_key):
    return AlphaVantageDataProvider(api_key)


@pytest.fixture
def av_price_mock_url(av_base_api_url, ticker, api_key):
    params = {
        "symbol": ticker,
        "apikey": api_key,
        "datatype": "json",
        "outputsize": "full",
        "function": "TIME_SERIES_DAILY",
    }
    encoded_query_params = urllib.parse.urlencode(params)
    return f"{av_base_api_url}{encoded_query_params}"


@responses.activate
def test_retrieve_price_data(data_provider, av_price_mock_url, ticker):
    responses.add(
        responses.GET,
        url=av_price_mock_url,
        json={
            "Meta Data": {
                "1. Information": "Daily Prices (open, high, low, close) and Volumes",
                "2. Symbol": ticker,
                "3. Last Refreshed": "2024-08-30",
                "4. Output Size": "Full",
                "5. Time Zone": "US/Eastern",
            },
            "Time Series (Daily)": {
                "2024-08-30": {
                    "1. open": "199.1100",
                    "2. high": "202.1700",
                    "3. low": "198.7300",
                    "4. close": "202.1300",
                    "5. volume": "4750999",
                },
                "2024-08-29": {
                    "1. open": "199.3000",
                    "2. high": "201.1200",
                    "3. low": "198.2700",
                    "4. close": "198.9000",
                    "5. volume": "2989594",
                },
            },
        },
        status=200,
        content_type="json",
    )

    df = data_provider.get_prices(ticker, output_size="full")
    assert isinstance(df.index, pd.DatetimeIndex)
    assert set(df.columns) == {
        OHLCV.Open,
        OHLCV.High,
        OHLCV.Low,
        OHLCV.Close,
        OHLCV.Volume,
    }

    pdt.assert_series_equal(
        left=df.loc["2024-08-30"],
        right=pd.Series(
            {
                OHLCV.Open: 199.1100,
                OHLCV.High: 202.1700,
                OHLCV.Low: 198.7300,
                OHLCV.Close: 202.1300,
                OHLCV.Volume: 4750999,
            }
        ),
        check_names=False,
    )


@pytest.fixture
def av_dividend_mock_url(av_base_api_url, api_key, ticker):
    params = {
        "symbol": ticker,
        "apikey": api_key,
        "function": "DIVIDENDS",
    }
    encoded_query_params = urllib.parse.urlencode(params)
    return f"{av_base_api_url}{encoded_query_params}"


@responses.activate
def test_retrieve_dividend_data(data_provider, av_dividend_mock_url, ticker):
    responses.add(
        responses.GET,
        url=av_dividend_mock_url,
        json={
            "symbol": ticker,
            "data": [
                {
                    "ex_dividend_date": "2024-08-09",
                    "declaration_date": "2024-07-29",
                    "record_date": "2024-08-09",
                    "payment_date": "2024-09-10",
                    "amount": "1.67",
                },
                {
                    "ex_dividend_date": "2024-05-09",
                    "declaration_date": "2024-04-30",
                    "record_date": "2024-05-10",
                    "payment_date": "2024-06-10",
                    "amount": "1.71",
                },
            ],
        },
        status=200,
        content_type="application/json",
    )

    expected = pd.DataFrame(
        data={
            Fields.Dividends: [1.67, 1.71],
            Fields.Date: [pd.to_datetime(x) for x in ["2024-08-09", "2024-05-09"]],
        }
    ).set_index(Fields.Date)

    actual = data_provider.get_dividends(ticker)

    pdt.assert_frame_equal(actual, expected)
