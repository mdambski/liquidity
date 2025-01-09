import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AssetTypes(str, Enum):
    Stock = "Stock"
    ETF = "ETF"
    Index = "Index"
    Crypto = "Crypto"
    Treasury = "Treasury"


@dataclass
class AssetMetadata:
    ticker: str
    name: str
    type: AssetTypes
    subtype: str
    maturity: Optional[str] = None
    currency: Optional[str] = None
    start_date: Optional[datetime.date] = None
    distributing: bool = False
    distribution_frequency: int = 0

    @property
    def is_yield(self) -> bool:
        """Returns if asset price represents yield."""
        return self.type == AssetTypes.Treasury and self.subtype == "Yield"
