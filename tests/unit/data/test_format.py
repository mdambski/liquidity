import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from liquidity.data.format import ensure_dataframe_sorted


class TestEnsureDataFrameSorted:
    @pytest.fixture
    def dates_increasing(self):
        return pd.DataFrame(
            {"A": [10, 2, 3]},
            index=pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
        )

    @pytest.fixture
    def dates_decreasing(self):
        return pd.DataFrame(
            {"A": [3, 2, 10]},
            index=pd.to_datetime(["2025-01-03", "2025-01-02", "2025-01-01"]),
        )

    @pytest.fixture
    def dates_unsorted(self):
        return pd.DataFrame(
            {"A": [2, 3, 10]},
            index=pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-01"]),
        )

    @pytest.fixture
    def empty(self):
        return pd.DataFrame(columns=["A"], index=pd.to_datetime([]))

    def test_ascending(self, dates_increasing):
        assert_frame_equal(ensure_dataframe_sorted(dates_increasing), dates_increasing)

    def test_descending(self, dates_decreasing):
        expected = pd.DataFrame(
            {"A": [10, 2, 3]},
            index=pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
        )
        assert_frame_equal(ensure_dataframe_sorted(dates_decreasing), expected)

    def test_unsorted(self, dates_unsorted):
        expected = pd.DataFrame(
            {"A": [10, 2, 3]},
            index=pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
        )
        assert_frame_equal(ensure_dataframe_sorted(dates_unsorted), expected)

    def test_empty_df(self, empty):
        assert_frame_equal(ensure_dataframe_sorted(empty), empty)
