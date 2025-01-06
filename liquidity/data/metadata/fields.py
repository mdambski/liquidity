from enum import StrEnum, auto


class Fields(StrEnum):
    Date = auto()
    Dividends = auto()
    TTM_Dividend = auto()
    Yield = auto()
    Spread = auto()


class OHLCV(StrEnum):
    Open = auto()
    High = auto()
    Low = auto()
    Close = auto()
    Volume = auto()
    Price = Close
