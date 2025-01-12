from datetime import timedelta

import pandas as pd

from liquidity.data.metadata.fields import Fields


def compute_ttm_dividend(
    df: pd.DataFrame, dividend_frequency: int, partial_window: bool = False
) -> pd.DataFrame:
    """Return dividends dataframe with computed TTM Dividend column.

    Parameters
    ----------
    df: DataFrame
        dividend dataframe.
    dividend_frequency: int
        How often the dividend is paid
    partial_window: bool
        Should sums for partially filled time window be returned. By default, excluded.
        This is related to the first year of data. If there are multiple dividends paid
        a year, then during this period the rolling sum will represent not the entire
        year, but a part of the year. In such cases the TTM dividend yield will not be
        representative of the entire year.
    """
    df[Fields.TTM_Dividend] = (
        df[Fields.Dividends].rolling("365D", min_periods=dividend_frequency).sum()
    )

    if not partial_window:
        offset = df.index[0] + timedelta(days=365) - timedelta(seconds=1)
        return df.loc[offset:]

    return df
