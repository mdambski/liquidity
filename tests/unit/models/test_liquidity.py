from unittest import mock

import numpy as np
import pandas as pd
import pytest

from liquidity.data.metadata.entities import FredEconomicData
from liquidity.models.liquidity import GlobalLiquidity

# ---------------------------------------------------------
# Fixtures to mock FredEconomicDataProvider
# ---------------------------------------------------------


@pytest.fixture
def mock_provider():
    """
    Provides a mocked FredEconomicDataProvider
    whose get_data() and get_metadata() return dummy data.
    """
    provider = mock.Mock()

    def get_metadata(ticker):
        return FredEconomicData(
            ticker=ticker,
            name=ticker,
            unit="Billions",
            currency="USD",
        )

    provider.get_metadata.side_effect = get_metadata

    return provider


@pytest.mark.parametrize(
    "ecb, walcl, wresbal, rrpon, wtregen, expected_liquidity",
    [
        # Scenario 1: all zeros
        (0, 0, 0, 0, 0, 0),
        # Scenario 2: only positive series active
        (10, 20, 30, 0, 0, 60),
        # Scenario 3: only negative series active
        (0, 0, 0, 40, 50, -90),
        # Scenario 4: mix of positives and negatives
        (5, 15, 25, 10, 20, 15),
        # Scenario 5: big positives vs big negatives
        (100, 200, 300, 150, 250, 200),
    ],
)
def test_liquidity_index_calculation(
    mock_provider,
    ecb,
    walcl,
    wresbal,
    rrpon,
    wtregen,
    expected_liquidity,
):
    """
    Tests that GlobalLiquidity correctly sums positive and negative series
    across various scenarios.
    """

    # Create dummy timeseries for all series
    dates = pd.date_range(start="2020-01-01", periods=3, freq="W")

    def make_series(value):
        return pd.DataFrame({"Close": np.full(3, value)}, index=dates)

    series_mapping = {
        "ECBASSETSW": make_series(ecb),
        "WALCL": make_series(walcl),
        "WRESBAL": make_series(wresbal),
        "RRPONTSYD": make_series(rrpon),
        "WTREGEN": make_series(wtregen),
    }

    def get_data(ticker):
        return series_mapping[ticker]

    mock_provider.get_data.side_effect = get_data

    # Initialize the model
    model = GlobalLiquidity(
        start_date=dates[0],
        end_date=dates[-1],
        provider=mock_provider,
    )

    df = model.df

    liquidity_series = df["Liquidity Index"]

    # Check all values in Liquidity Index equal expected_liquidity
    assert all(np.isclose(liquidity_series.values, expected_liquidity)), (
        f"Liquidity Index was {liquidity_series.values}, " f"expected {expected_liquidity}"
    )
