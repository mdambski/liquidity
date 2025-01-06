import abc
import pandas as pd


class DataProviderBase(abc.ABC):
    @abc.abstractmethod
    def get_prices(self, ticker: str) -> pd.DataFrame:
        raise NotImplementedError

    @abc.abstractmethod
    def get_dividends(self, ticker: str) -> pd.DataFrame:
        raise NotImplementedError
