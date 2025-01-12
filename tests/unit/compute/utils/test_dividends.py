import numpy.testing as npt
import pandas as pd
import pytest

from liquidity.compute.utils.dividends import compute_ttm_dividend
from liquidity.data.metadata.fields import Fields

TTM_DIVIDEND_EXPECTED = f"{Fields.TTM_Dividend}_expected"
IS_FULL_WINDOW = "IS_FULL_WINDOW"


@pytest.fixture
def q_div_with_special():
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


def test_reqular_dividends(q_div_with_special):
    expected = q_div_with_special[[TTM_DIVIDEND_EXPECTED]]
    actual = compute_ttm_dividend(df=q_div_with_special, partial_window=True)

    npt.assert_almost_equal(
        actual=actual[Fields.TTM_Dividend].values,
        desired=expected[TTM_DIVIDEND_EXPECTED].values,
        decimal=4,
    )
