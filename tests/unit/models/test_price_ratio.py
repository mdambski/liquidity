import pandas as pd
import pytest

from liquidity.models.price_ratio import PriceRatio


class MockTicker:
    def __init__(self, name, prices):
        self.name = name
        self.prices = prices

    @staticmethod
    def from_name(name):
        data = {
            "ETH": pd.DataFrame(
                {"Close": [1400.5, 1350.25, 1425.0]},
                index=pd.date_range("2023-01-01", periods=3),
            ),
            "BTC": pd.DataFrame(
                {"Close": [18000.25, 17500.5, 18500.0]},
                index=pd.date_range("2023-01-01", periods=3),
            ),
        }
        prices = data.get(name, pd.DataFrame())
        return MockTicker(name, prices)


@pytest.fixture
def mock_tickers(monkeypatch):
    monkeypatch.setattr("liquidity.models.price_ratio.Ticker", MockTicker)


class TestPriceRatio:
    def test_price_ratio_df(self, mock_tickers):
        ratio = PriceRatio("ETH", "BTC")
        expected = pd.DataFrame(
            {
                "CloseETH": [1400.5, 1350.25, 1425.0],
                "CloseBTC": [18000.25, 17500.5, 18500.0],
                "Ratio": [
                    1400.5 / 18000.25,
                    1350.25 / 17500.5,
                    1425.0 / 18500.0,
                ],
            },
            index=pd.date_range("2023-01-01", periods=3),
        )
        pd.testing.assert_frame_equal(ratio.df, expected)

    def test_price_ratio_partial_data(self, mock_tickers):
        ratio = PriceRatio("ETH", "BTC")

        ratio.ticker.prices.loc["2023-01-03"] = None
        expected = pd.DataFrame(
            {
                "CloseETH": [1400.5, 1350.25],
                "CloseBTC": [18000.25, 17500.5],
                "Ratio": [
                    1400.5 / 18000.25,
                    1350.25 / 17500.5,
                ],
            },
            index=pd.date_range("2023-01-01", periods=2),
        )

        pd.testing.assert_frame_equal(ratio.df, expected)
