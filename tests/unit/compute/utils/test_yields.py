import pandas as pd
import pytest

from liquidity.compute.utils.yields import compute_dividend_yield
from liquidity.data.metadata.fields import OHLCV, Fields


@pytest.fixture
def sample_prices():
    data = {
        OHLCV.Close: [100, 105, 110, 115],
    }
    index = pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"])
    return pd.DataFrame(data, index=index)


@pytest.fixture
def sample_dividends():
    data = {
        Fields.TTM_Dividend: [2, None, 3, None],
    }
    index = pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"])
    return pd.DataFrame(data, index=index)


def test_compute_dividend_yield(sample_prices, sample_dividends):
    result = compute_dividend_yield(sample_prices, sample_dividends)

    # Expected yield calculations
    expected_yield = [
        (2 / 100) * 100,  # 2025-01-01
        (2 / 105) * 100,  # 2025-01-02
        (3 / 110) * 100,  # 2025-01-03
        (3 / 115) * 100,  # 2025-01-04
    ]
    expected_index = pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"])
    expected = pd.DataFrame({Fields.Yield: expected_yield}, index=expected_index)

    pd.testing.assert_frame_equal(result, expected)


def test_missing_data_in_prices(sample_dividends):
    prices = pd.DataFrame({OHLCV.Close: [None, None, None, None]}, index=sample_dividends.index)
    with pytest.raises(TypeError):
        compute_dividend_yield(prices, sample_dividends)


def test_no_dividends(sample_prices):
    dividends = pd.DataFrame(
        {Fields.TTM_Dividend: [None, None, None, None]}, index=sample_prices.index
    )
    result = compute_dividend_yield(sample_prices, dividends)

    # There are no dividends so expected yield is 0
    expected = pd.DataFrame({Fields.Yield: [0.0, 0.0, 0.0, 0.0]}, index=sample_prices.index)
    pd.testing.assert_frame_equal(result, expected)
