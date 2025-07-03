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


@pytest.fixture
def dummy_eur_series():
    """
    Provides a dummy EUR-denominated time series.
    """
    dates = pd.date_range(start="2020-01-01", periods=5, freq="W")
    data = pd.DataFrame(
        {"Close": [10, 20, 30, 40, 50]},
        index=dates,
    )
    return data


def get_fx_series(exchange_rate, dates):
    """
    Provides a dummy exchange rate.
    """
    data = pd.DataFrame(
        {"Close": [exchange_rate] * len(dates)},
        index=dates,
    )
    return data


@pytest.mark.parametrize(
    "currency_from, unit_from, fx_ticker, fx_rate, input_values, expected_values",
    [
        # Case 1: USD, different unit (Millions -> Billions)
        (
            "USD",
            "Millions",
            None,
            None,
            [1000, 2000, 3000, 4000, 5000],  # Millions
            [1.0, 2.0, 3.0, 4.0, 5.0],  # Billions
        ),
        # Case 2: USD, different unit (Trillions -> Billions)
        (
            "USD",
            "Trillions",
            None,
            None,
            [1.0, 2.0, 3.0, 4.0, 5.0],  # Trillions
            [1000, 2000, 3000, 4000, 5000],  # Billions
        ),
        # Case 2: EUR, same unit (Billions)
        (
            "EUR",
            "Billions",
            "DEXUSEU",
            1.2,
            [10, 20, 30, 40, 50],
            [12.0, 24.0, 36.0, 48.0, 60.0],  # EUR * 1.2 -> USD
        ),
        # Case 3: JPY, different unit (Trillions -> Billions)
        (
            "JPY",
            "Trillions",
            "DEXJPUS",
            150.0,
            [2, 4, 6, 8, 10],  # trillions JPY
            [
                2_000 / 150.0,
                4_000 / 150.0,
                6_000 / 150.0,
                8_000 / 150.0,
                10_000 / 150.0,
            ],  # trillions JPY -> billions USD
        ),
    ],
)
def test_standardize_series(
    mock_provider,
    dummy_eur_series,
    currency_from,
    unit_from,
    fx_ticker,
    fx_rate,
    input_values,
    expected_values,
):
    """
    Tests _standardize_series for:
    - unit conversion (Millions, Trillions)
    - currency conversion (EUR->USD, JPY->USD)
    """

    # Prepare dummy data with given input values
    dates = dummy_eur_series.index

    input_series = pd.DataFrame({"Close": input_values}, index=dates)

    def get_data_side_effect(ticker):
        if ticker == fx_ticker:
            return get_fx_series(fx_rate, dates)
        raise ValueError(f"Unexpected ticker: {ticker}")

    mock_provider.get_data.side_effect = get_data_side_effect

    # Metadata
    mock_provider.get_metadata.return_value = FredEconomicData(
        ticker=fx_ticker,
        name=fx_ticker,
        unit=unit_from,
        currency=currency_from,
    )

    # Instantiate the model
    gl = GlobalLiquidity(provider=mock_provider)

    # Call _standardize_series
    standardized = gl._standardize_series(
        input_series.copy(),
        column="Close",
        metadata=mock_provider.get_metadata.return_value,
    )

    # Check values
    pd.testing.assert_series_equal(
        standardized["Close"],
        pd.Series(expected_values, index=dates),
        check_names=False,
        check_dtype=False,
    )
