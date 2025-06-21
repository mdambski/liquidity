import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AssetTypes(str, Enum):
    Stock = "Stock"
    ETF = "ETF"
    Index = "Index"
    Crypto = "Crypto"
    Treasury = "Treasury"
    EconomicData = "EconomicData"


@dataclass
class Metadata:
    ticker: str
    name: str
    type: AssetTypes


@dataclass
class FredEconomicData(Metadata):
    unit: str
    currency: str
    type: AssetTypes = field(default=AssetTypes.EconomicData, init=False)


@dataclass
class AssetMetadata(Metadata):
    type: AssetTypes
    subtype: str
    maturity: Optional[str] = None
    currency: Optional[str] = None
    start_date: Optional[datetime.date] = None
    distributing: bool = False
    distribution_frequency: int = 0

    @property
    def is_treasury_yield(self) -> bool:
        """Returns if asset price represents yield."""
        return self.type == AssetTypes.Treasury and self.subtype == "Yield"
