from typing import Callable

import pandas as pd


def formatter_factory(
    cols_mapper: dict = None,
    index_col: str = None,
    index_name: str = None,
    cols_out: list[str] = None,
    to_numeric: list[str] = None,
    ensure_sorted: bool = True,
) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Returns formatter func for dataframe post-processing."""

    def format_func(df):
        if cols_mapper:
            df = df.rename(cols_mapper, axis=1)
        if index_col:
            df = df.set_index(pd.to_datetime(df[index_col]))
        if to_numeric:
            df[to_numeric] = df[to_numeric].apply(pd.to_numeric)
        if ensure_sorted:
            df = ensure_dataframe_sorted(df)

        index_new_name = index_name or index_col
        if index_new_name:
            df.index.name = index_new_name

        return df[cols_out] if cols_out else df

    return format_func


def ensure_dataframe_sorted(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure dataframe index is sorted. This is important
    for some computations (i.e. ttm dividend calculation)
    """
    if df.index.is_monotonic_increasing:
        # already sorted
        return df

    if df.index.is_monotonic_decreasing:
        # if sort order is decreasing - flip it.
        # Faster than sorting with O(n) complexity.
        return df[::-1]

    # if unsorted execute sorting, with O(n log n) complexity.
    return df.sort_index()
