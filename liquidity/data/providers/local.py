import os
from pathlib import Path

import pandas as pd
from data.metadata.fields import OHLCV, Fields

from liquidity.data.format import formatter_factory
from liquidity.data.providers.base import DataProviderBase
from liquidity.exceptions import DataNotAvailable

DATA_DIR = Path(__file__).parent.parent / "data"


class LocalStorageDataProvider(DataProviderBase):
    name = "local"

    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir

    def _load(self, path: str) -> pd.DataFrame:
        if not os.path.exists(path):
            raise DataNotAvailable(
                f"Missing data for ticker. Make "
                f"sure the data is available at "
                f"the path: {path}"
            )
        return pd.read_csv(path)

    def get_prices(self, ticker: str) -> pd.DataFrame:
        file_path = os.path.join(self.data_dir, ticker, "price.csv")
        formatter_func = formatter_factory(
            index_col=Fields.Date, cols_out=[OHLCV.Close]
        )
        return formatter_func(self._load(file_path))

    def get_dividends(self, ticker: str) -> pd.DataFrame:
        df = self._load(os.path.join(self.data_dir, ticker, "dividend.csv"))
        format_func = formatter_factory(index_col=Fields.Date)
        return format_func(df)

    def get_treasury_yield(self, maturity: str) -> pd.DataFrame:
        raise NotImplementedError
