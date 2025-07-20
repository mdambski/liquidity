from enum import Enum
from typing import List


class StrEnum(str, Enum):
    """Mimics the behavior of StrEnum in Python 3.9"""

    pass


class Fields(StrEnum):
    Date = "Date"
    Dividends = "Dividends"
    TTM_Dividend = "TTM_Dividend"
    Yield = "Yield"
    Spread = "Spread"
    Ratio = "Ratio"


class OHLCV(StrEnum):
    Open = "Open"
    High = "High"
    Low = "Low"
    Close = "Close"
    Volume = "Volume"

    @classmethod
    def all_values(cls) -> List[str]:
        return [x.value for x in list(cls)]
