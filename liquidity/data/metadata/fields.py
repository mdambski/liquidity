from enum import Enum


class StrEnum(str, Enum):
    """Mimics the behavior of StrEnum in Python 3.9"""

    pass


class Fields(StrEnum):
    Date = "Date"
    Dividends = "Dividends"
    TTM_Dividend = "TTM_Dividend"
    Yield = "Yield"
    Spread = "Spread"


class OHLCV(StrEnum):
    Open = "Open"
    High = "High"
    Low = "Low"
    Close = "Close"
    Volume = "Volume"
    Price = Close
