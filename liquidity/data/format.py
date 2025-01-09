from typing import Callable

import pandas as pd


def formatter_factory(
    cols_mapper: dict = None,
    index_col: str = None,
    cols_out: list[str] = None,
    to_numeric: list[str] = None,
) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Returns formatter func for dataframe post-processing."""

    def format_func(df):
        if cols_mapper:
            df = df.rename(cols_mapper, axis=1)
        if index_col:
            df = df.set_index(pd.to_datetime(df[index_col]))
        if to_numeric:
            df[to_numeric] = df[to_numeric].apply(pd.to_numeric)
        return df[cols_out] if cols_out else df

    return format_func
