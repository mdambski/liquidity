from typing import Callable, Dict, Optional

import pandas as pd


def formatter_factory(
    cols_mapper: Optional[Dict[str, str]] = None,
    index_col: Optional[str] = None,
    index_name: Optional[str] = None,
    cols_out: Optional[list[str]] = None,
    to_numeric: Optional[list[str]] = None,
    ensure_sorted: bool = True,
) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Returns a formatter function for dataframe post-processing.

    Parameters
    ----------
        cols_mapper (dict, optional): Column renaming mapping.
        index_col (str, optional): Column to use as the index.
        index_name (str, optional): New name for the index.
        cols_out (list[str], optional): List of columns to keep in the final dataframe.
        to_numeric (list[str], optional): Columns to convert to numeric types.
        ensure_sorted (bool): Whether to ensure the dataframe is sorted by its index.

    Returns
    -------
        Callable[[pd.DataFrame], pd.DataFrame]: A function to format dataframes.

    """

    def format_func(df: pd.DataFrame) -> pd.DataFrame:
        if cols_mapper:
            df = df.rename(cols_mapper, axis=1)

        if index_col:
            df = df.set_index(pd.to_datetime(df[index_col]))

        if to_numeric:
            df[to_numeric] = df[to_numeric].apply(pd.to_numeric)

        if ensure_sorted:
            df = ensure_dataframe_sorted(df)

        if index_name or index_col:
            df.index.name = index_name or index_col

        return df[cols_out] if cols_out else df

    return format_func


def ensure_dataframe_sorted(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure dataframe index is sorted.

    Parameters
    ----------
        df (pd.DataFrame): Input dataframe.

    Returns
    -------
        pd.DataFrame: Dataframe with a sorted index.

    """
    if df.index.is_monotonic_increasing:
        return df

    if df.index.is_monotonic_decreasing:
        return df[::-1]

    return df.sort_index()
