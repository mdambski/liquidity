from collections import namedtuple
from unittest import mock

import numpy as np
import pandas as pd
import pytest

from liquidity.data.metadata.entities import FredEconomicData
from liquidity.models.liquidity import GlobalLiquidity


@pytest.fixture
def mock_provider():
    """Provides a mocked FredEconomicDataProvider
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


@pytest.fixture
def liquidity_dates():
    """Provides a fixed date range for liquidity tests."""
    return pd.date_range(start="2020-01-01", periods=3, freq="W")


@pytest.fixture
def liquidity_series_factory(liquidity_dates):
    """Returns a function to create a constant time series DataFrame."""

    def _make(value):
        return pd.DataFrame(
            {"Close": np.full(len(liquidity_dates), value)},
            index=liquidity_dates,
        )

    return _make


LiquidityTestCase = namedtuple(
    "LiquidityTestCase",
    ["ecb", "walcl", "wresbal", "rrpon", "wtregen", "expected_liquidity", "description"],
)

LIQUIDITY_TEST_CASES = [
    LiquidityTestCase(
        ecb=0,
        walcl=0,
        wresbal=0,
        rrpon=0,
        wtregen=0,
        expected_liquidity=0,
        description="All zeros",
    ),
    LiquidityTestCase(
        ecb=10,
        walcl=20,
        wresbal=30,
        rrpon=0,
        wtregen=0,
        expected_liquidity=60,
        description="Only positive series active",
    ),
    LiquidityTestCase(
        ecb=0,
        walcl=0,
        wresbal=0,
        rrpon=40,
        wtregen=50,
        expected_liquidity=-90,
        description="Only negative series active",
    ),
    LiquidityTestCase(
        ecb=5,
        walcl=15,
        wresbal=25,
        rrpon=10,
        wtregen=20,
        expected_liquidity=15,
        description="Mix of positives and negatives",
    ),
    LiquidityTestCase(
        ecb=100,
        walcl=200,
        wresbal=300,
        rrpon=150,
        wtregen=250,
        expected_liquidity=200,
        description="Big positives vs big negatives",
    ),
]


@pytest.mark.parametrize(
    "case",
    LIQUIDITY_TEST_CASES,
    ids=[c.description for c in LIQUIDITY_TEST_CASES],
)
def test_liquidity_index_calculation(
    mock_provider,
    liquidity_dates,
    liquidity_series_factory,
    case,
):
    """Tests that GlobalLiquidity correctly sums positive and negative series
    across different scenarios.
    """
    # Create dummy timeseries for each ticker
    series_mapping = {
        "ECBASSETSW": liquidity_series_factory(case.ecb),
        "WALCL": liquidity_series_factory(case.walcl),
        "WRESBAL": liquidity_series_factory(case.wresbal),
        "RRPONTSYD": liquidity_series_factory(case.rrpon),
        "WTREGEN": liquidity_series_factory(case.wtregen),
    }

    def get_data(ticker):
        return series_mapping[ticker]

    mock_provider.get_data.side_effect = get_data

    # Initialize the model
    model = GlobalLiquidity(
        start_date=liquidity_dates[0],
        end_date=liquidity_dates[-1],
        provider=mock_provider,
    )

    # Extract the Liquidity Index
    liquidity_series = model.df["Liquidity Index"]

    # Assert all values match the expected liquidity
    assert all(np.isclose(liquidity_series.values, case.expected_liquidity)), (
        f"Liquidity Index was {liquidity_series.values}, " f"expected {case.expected_liquidity}"
    )


@pytest.fixture
def dates():
    return pd.date_range(start="2020-01-01", periods=5, freq="W")


@pytest.fixture
def dummy_eur_series(dates):
    return pd.DataFrame(
        {"Close": [10, 20, 30, 40, 50]},
        index=dates,
    )


@pytest.fixture
def fx_series_factory():
    def _factory(rate, dates):
        rates = rate if isinstance(rate, list) else [rate] * len(dates)
        return pd.DataFrame({"Close": rates}, index=dates)

    return _factory


StandarizeTestCase = namedtuple(
    "TestCase",
    [
        "currency_from",
        "unit_from",
        "fx_ticker",
        "fx_rate",
        "input_values",
        "expected_values",
        "description",
    ],
)

TEST_CASES = [
    StandarizeTestCase(
        currency_from="USD",
        unit_from="Millions",
        fx_ticker=None,
        fx_rate=None,
        input_values=[1000, 2000, 3000, 4000, 5000],
        expected_values=[1.0, 2.0, 3.0, 4.0, 5.0],
        description="USD, Millions -> Billions",
    ),
    StandarizeTestCase(
        currency_from="USD",
        unit_from="Trillions",
        fx_ticker=None,
        fx_rate=None,
        input_values=[1.0, 2.0, 3.0, 4.0, 5.0],
        expected_values=[1000, 2000, 3000, 4000, 5000],
        description="USD, Trillions -> Billions",
    ),
    StandarizeTestCase(
        currency_from="EUR",
        unit_from="Billions",
        fx_ticker="DEXUSEU",
        fx_rate=1.2,
        input_values=[10, 20, 30, 40, 50],
        expected_values=[12.0, 24.0, 36.0, 48.0, 60.0],
        description="EUR, Billions -> USD",
    ),
    StandarizeTestCase(
        currency_from="JPY",
        unit_from="Trillions",
        fx_ticker="DEXJPUS",
        fx_rate=150.0,
        input_values=[2, 4, 6, 8, 10],
        expected_values=[
            2000 / 150.0,
            4000 / 150.0,
            6000 / 150.0,
            8000 / 150.0,
            10000 / 150.0,
        ],
        description="JPY, Trillions -> Billions USD",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=[c.description for c in TEST_CASES])
def test_standardize_series(
    mock_provider,
    dummy_eur_series,
    fx_series_factory,
    dates,
    case,
):
    """Test _standardize_series for:
    - unit conversion (e.g. Millions -> Billions, Trillions -> Billions)
    - currency conversion via FX rates
    """
    # Create input series with specified values
    input_series = pd.DataFrame(
        {"Close": case.input_values},
        index=dates,
    )

    # Prepare FX side-effect if applicable
    if case.fx_ticker:

        def side_effect(ticker):
            if ticker == case.fx_ticker:
                return fx_series_factory(case.fx_rate, dates)
            else:
                pytest.fail(f"Unexpected ticker requested: {ticker}")

        mock_provider.get_data.side_effect = side_effect
    else:
        mock_provider.get_data.side_effect = None

    # Prepare metadata
    metadata = FredEconomicData(
        ticker=case.fx_ticker,
        name=case.fx_ticker,
        unit=case.unit_from,
        currency=case.currency_from,
    )

    mock_provider.get_metadata.return_value = metadata

    # Instantiate GlobalLiquidity model
    gl = GlobalLiquidity(provider=mock_provider)

    # Perform standardization
    standardized = gl._standardize_series(
        input_series.copy(),
        column="Close",
        metadata=metadata,
    )

    # Assert the output values
    pd.testing.assert_series_equal(
        standardized["Close"],
        pd.Series(case.expected_values, index=dates),
        check_names=False,
        check_dtype=False,
    )


def test_currency_conversion_with_misaligned_dates(mock_provider, fx_series_factory, dates):
    """Verify currency conversion aligns FX rates by date and drops missing."""
    # Main data: denominated in EUR with weekly intervals
    data_series = pd.DataFrame({"Close": [10, 20, 30, 40, 50]}, index=dates)

    # FX series with EUR/USD daily rates, some points
    # are before and some after the weekly datapoints
    # only two overlap.
    fx_series = pd.DataFrame(
        {"Close": [1.0, 1.1, 1.2, 1.3]},
        index=pd.DatetimeIndex(
            [
                dates[0] - pd.Timedelta(days=1),
                dates[0],
                dates[1],
                dates[1] + pd.Timedelta(days=1),
            ]
        ),
    )

    # Setup mocks and metadata
    mock_provider.get_data.return_value = fx_series
    metadata = FredEconomicData(
        ticker="TEST_EUR_SERIES",
        name="EUR Series",
        unit="Billions",
        currency="EUR",  # currency_from
    )
    mock_provider.get_metadata.return_value = metadata

    # Run standardization logic
    gl = GlobalLiquidity(provider=mock_provider)
    actual = gl._standardize_series(data_series.copy(), "Close", metadata)

    # Evaluate the result
    expected = pd.Series([11.0, 24.0], index=[dates[0], dates[1]])
    pd.testing.assert_series_equal(actual["Close"], expected, check_names=False)
