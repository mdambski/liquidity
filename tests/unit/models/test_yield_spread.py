import pandas as pd
import pytest

from liquidity.models.yield_spread import YieldSpread
from liquidity.compute.utils.yields import compute_dividend_yield
from liquidity.data.metadata.entities import AssetMetadata, AssetTypes


class MockTicker:
    def __init__(self, symbol, prices, dividends):
        self.symbol = symbol
        self._prices = prices
        self._dividends = dividends
        self.metadata = AssetMetadata(
            ticker=symbol,
            name=symbol,
            type=AssetTypes.ETF,
            subtype="Bonds",
            currency="USD",
            distributing=True,
            distribution_frequency=12,
        )

    @property
    def prices(self):
        return self._prices

    @property
    def dividends(self):
        return self._dividends

    @property
    def yields(self):
        return compute_dividend_yield(self.prices, self.dividends)

    @staticmethod
    def for_symbol(symbol: str):
        idx = pd.date_range("2023-01-01", periods=3)
        data = {
            "HYG": {
                "prices": pd.DataFrame({"Close": [100, 100, 100]}, index=idx),
                "dividends": pd.DataFrame({"TTM_Dividend": [5.5, 5.48, 5.51]}, index=idx)
            },
            "LQD": {
                "prices": pd.DataFrame({"Close": [100, 100, 100]}, index=idx),
                "dividends": pd.DataFrame({"TTM_Dividend": [3.2, 3.25, 3.19]}, index=idx)
            }
        }
        return MockTicker(
            symbol,
            prices=data[symbol]["prices"],
            dividends=data[symbol]["dividends"],
        )


@pytest.fixture
def mock_tickers(monkeypatch):
    monkeypatch.setattr("liquidity.models.yield_spread.Ticker", MockTicker)


class TestYieldSpread:
    def test_calculation(self, mock_tickers):
        spread = YieldSpread("HYG", "LQD")
        expected = pd.DataFrame(
            {
                "YieldHYG": [5.5, 5.48, 5.51],
                "YieldLQD": [3.2, 3.25, 3.19],
                "Spread": [
                    5.5 - 3.2,
                    5.48 - 3.25,
                    5.51 - 3.19,
                ],
            },
            index=pd.date_range("2023-01-01", periods=3),
        )
        pd.testing.assert_frame_equal(spread.df, expected)
