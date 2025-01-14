import json
import urllib.parse

import pandas as pd
import pytest
import responses
from pandas import testing as pdt


class TestTreasuryYieldData:
    @pytest.fixture
    def api_url(self, av_base_api_url, api_key):
        params = {
            "apikey": api_key,
            "interval": "monthly",
            "maturity": "10year",
            "datatype": "json",
            "function": "TREASURY_YIELD",
        }
        return "?".join([av_base_api_url, urllib.parse.urlencode(params)])

    @pytest.fixture
    def api_response_json(self, treasury_yield_fixture_path):
        with open(treasury_yield_fixture_path, mode="r") as f:
            data = json.load(f)
        return data

    @responses.activate
    def test_treasury_yield_data(self, av_data_provider, api_url, api_response_json):
        responses.add(
            responses.GET,
            url=api_url,
            json=api_response_json,
            status=200,
            content_type="json",
        )

        df = av_data_provider.get_treasury_yield(maturity="10year")

        assert df.shape == (24, 1)
        assert set(df.columns) == {"Yield"}
        assert isinstance(df.index, pd.DatetimeIndex)

        # check if selected fields match and have correct format
        pdt.assert_frame_equal(
            df.loc[["2024-12-01", "2023-01-01"]],
            pd.DataFrame(
                data={
                    "Yield": [4.39, 3.53],
                    "Date": [pd.to_datetime(x) for x in ["2024-12-01", "2023-01-01"]],
                }
            ).set_index("Date"),
            check_names=False,
        )


class TestPriceData:
    @pytest.fixture
    def api_url(self, av_base_api_url, api_key, ticker):
        params = {
            "symbol": ticker,
            "apikey": api_key,
            "datatype": "json",
            "outputsize": "full",
            "function": "TIME_SERIES_DAILY",
        }
        return "?".join([av_base_api_url, urllib.parse.urlencode(params)])

    @pytest.fixture
    def api_response_json(self, ticker):
        return {
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
        }

    @responses.activate
    def test_price_data(self, av_data_provider, api_url, api_response_json, ticker):
        responses.add(
            responses.GET,
            url=api_url,
            json=api_response_json,
            status=200,
            content_type="json",
        )

        df = av_data_provider.get_prices(ticker, output_size="full")

        assert df.shape == (2, 5)
        assert isinstance(df.index, pd.DatetimeIndex)
        assert set(df.columns) == {"Open", "Close", "Low", "High", "Volume"}

        expected_df = pd.DataFrame(
            data={
                "Open": [199.3000, 199.1100],
                "High": [201.1200, 202.1700],
                "Low": [198.2700, 198.7300],
                "Close": [198.9000, 202.1300],
                "Volume": [2989594.0, 4750999.0],
            },
            index=pd.DatetimeIndex(
                data=pd.to_datetime(["2024-08-29", "2024-08-30"]), name="Date"
            ),
        )

        pdt.assert_frame_equal(df, expected_df)


class TestDividendData:
    @pytest.fixture
    def api_url(self, av_base_api_url, api_key, ticker):
        params = {
            "symbol": ticker,
            "apikey": api_key,
            "function": "DIVIDENDS",
        }
        return "?".join([av_base_api_url, urllib.parse.urlencode(params)])

    @pytest.fixture
    def api_response_json(self, ticker):
        return {
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
        }

    @responses.activate
    def test_dividend_data(self, av_data_provider, api_url, api_response_json, ticker):
        responses.add(
            responses.GET,
            url=api_url,
            json=api_response_json,
            status=200,
            content_type="application/json",
        )

        df = av_data_provider.get_dividends(ticker)

        assert df.shape == (2, 1)
        assert isinstance(df.index, pd.DatetimeIndex)

        expected_df = pd.DataFrame(
            data={"Dividends": [1.71, 1.67]},
            index=pd.DatetimeIndex(
                data=pd.to_datetime(["2024-05-09", "2024-08-09"]), name="Date"
            ),
        )

        pdt.assert_frame_equal(df, expected_df)
