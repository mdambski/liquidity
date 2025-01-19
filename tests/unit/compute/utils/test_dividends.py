import pandas as pd
import pytest

from liquidity.compute.utils.dividends import compute_ttm_dividend
from liquidity.data.metadata.fields import Fields

TTM_DIVIDEND_EXPECTED = f"{Fields.TTM_Dividend}_expected"


@pytest.fixture
def div_data():
    """Increasing quarterly dividend with on-off special distribution"""
    df = pd.DataFrame(
        data=[
            ["2000-01-02", 0.25, 0.25, False],
            ["2000-04-02", 0.26, 0.51, False],
            ["2000-07-02", 0.27, 0.78, False],
            ["2000-10-02", 0.27, 1.05, False],
            ["2000-12-15", 0.10, 1.15, False],  # special dividend
            ["2001-01-02", 0.28, 1.18, True],
            ["2001-04-02", 0.29, 1.21, True],
            ["2001-07-02", 0.30, 1.24, True],
            ["2001-10-02", 0.30, 1.27, True],
            ["2002-01-02", 0.30, 1.19, True],
            ["2002-04-02", 0.31, 1.21, True],
            ["2002-07-02", 0.31, 1.22, True],
            ["2002-10-02", 0.31, 1.23, True],
        ],
        columns=[Fields.Date, Fields.Dividends, TTM_DIVIDEND_EXPECTED, "is_full_year"],
    )
    return df.set_index(pd.to_datetime(df[Fields.Date]))


def test_regular_dividends(div_data):
    expected = div_data[[TTM_DIVIDEND_EXPECTED]]
    actual = compute_ttm_dividend(
        df=div_data, dividend_frequency=4, partial_window=True
    )

    pd.testing.assert_series_equal(
        actual[Fields.TTM_Dividend], expected[TTM_DIVIDEND_EXPECTED], check_names=False
    )


def test_regular_dividends_partial_false(div_data):
    expected = div_data[div_data["is_full_year"]][[TTM_DIVIDEND_EXPECTED]]
    actual = compute_ttm_dividend(df=div_data, dividend_frequency=4)

    pd.testing.assert_series_equal(
        actual[Fields.TTM_Dividend], expected[TTM_DIVIDEND_EXPECTED], check_names=False
    )


@pytest.fixture
def unsorted_dates_data():
    return pd.DataFrame(
        {
            Fields.Dividends: [0.5, 0.6, 0.7],
        },
        index=pd.to_datetime(["2025-02-01", "2025-01-01", "2025-03-01"]),
    )


@pytest.fixture
def descending_dates_data():
    return pd.DataFrame(
        {
            Fields.Dividends: [0.5, 0.6, 0.7],
        },
        index=pd.to_datetime(["2025-03-01", "2025-02-01", "2025-01-01"]),
    )


@pytest.mark.parametrize("data", ["unsorted_dates_data", "descending_dates_data"])
def test_error_for_invalid_dates_order(request, data):
    df = request.getfixturevalue(data)

    with pytest.raises(ValueError, match="Dates should be sorted in ascending order"):
        compute_ttm_dividend(df)
