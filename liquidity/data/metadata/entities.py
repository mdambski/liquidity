import datetime
from dataclasses import dataclass
from enum import StrEnum, auto


class AssetTypes(StrEnum):
    Stock = auto()
    ETF = auto()
    Index = auto()
    Crypto = auto()


@dataclass
class AssetMetadata:
    ticker: str
    name: str
    type: AssetTypes
    subtype: str
    currency: str | None = None
    start_date: datetime.date | None = None
    distributing: bool = False
    distribution_frequency: int = 0

    @property
    def is_yield(self) -> bool:
        """Returns if asset price represents yield."""
        return self.type == AssetTypes.Index and self.subtype == "Yield"
