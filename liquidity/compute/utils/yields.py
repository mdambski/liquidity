import pandas as pd

from liquidity.data.metadata.fields import OHLCV, Fields


def compute_dividend_yield(
    prices: pd.DataFrame, dividends: pd.DataFrame
) -> pd.DataFrame:
    """Return yield dataframe calculated based on prices and dividends data."""
    df = prices.merge(dividends, how="left", left_index=True, right_index=True)

    # Forward fill values as the value of the calculated TTM_Dividend
    # is valid for all the dates until the next distribution takes place
    df[Fields.TTM_Dividend] = df[Fields.TTM_Dividend].ffill()

    def yield_formula(row):
        return (row[Fields.TTM_Dividend] / row[OHLCV.Price]) * 100.0

    df[Fields.Yield] = df.apply(yield_formula, axis=1)
    return df[[Fields.Yield]]
