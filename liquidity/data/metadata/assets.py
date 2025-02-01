from datetime import datetime
from typing import Optional

from liquidity.data.metadata.entities import (
    AssetMetadata,
    AssetTypes,
    FredEconomicData,
    Metadata,
)

ALL_DATA = {
    "HYG": AssetMetadata(
        ticker="HYG",
        name="iShares iBoxx $ High Yield Corporate Bond ETF",
        type=AssetTypes.ETF,
        subtype="Bonds",
        currency="USD",
        start_date=datetime(2007, 4, 4),
        distributing=True,
        distribution_frequency=12,
    ),
    "LQD": AssetMetadata(
        ticker="LQD",
        name="iShares iBoxx $ Investment Grade Corporate Bond ETF",
        type=AssetTypes.ETF,
        subtype="Bonds",
        currency="USD",
        start_date=datetime(2002, 7, 22),
        distributing=True,
        distribution_frequency=12,
    ),
    "UST-10Y": AssetMetadata(
        ticker="UST-10Y",
        name="Interest Rate On 10-Year US Treasury",
        type=AssetTypes.Treasury,
        subtype="Yield",
        maturity="10year",
    ),
    "SPY": AssetMetadata(
        ticker="SPY",
        name="SPDR S&P 500 ETF Trust",
        type=AssetTypes.ETF,
        currency="USD",
        subtype="Stocks",
        distributing=True,
        distribution_frequency=4,
    ),
    "QQQ": AssetMetadata(
        ticker="QQQ",
        name="Invesco QQQ Trust (Nasdaq-100)",
        type=AssetTypes.ETF,
        currency="USD",
        subtype="Stocks",
        distributing=True,
        distribution_frequency=4,
    ),
    "BTC": AssetMetadata(
        ticker="BTC",
        name="Bitcoin",
        currency="USD",
        type=AssetTypes.Crypto,
        subtype="Spot",
    ),
    "ETH": AssetMetadata(
        ticker="ETH",
        name="Ethereum",
        currency="USD",
        type=AssetTypes.Crypto,
        subtype="Spot",
    ),
    "WRESBAL": FredEconomicData(
        ticker="WRESBAL",
        name="Reserve Balances with FED Banks",
        currency="USD",
        unit="Billions",
    ),
    "WTREGEN": FredEconomicData(
        ticker="RRPONTSYD",
        name="Treasury General Account (TGA) Balance",
        currency="USD",
        unit="Billions",
    ),
    "RRPONTSYD": FredEconomicData(
        ticker="RRPONTSYD", name="Reverse Repo", currency="USD", unit="Billions"
    ),
    "WALCL": FredEconomicData(
        ticker="WALCL",
        name="US Federal Reserve (FED) Balance Sheet",
        currency="USD",
        unit="Millions",
    ),
    "ECBASSETSW": FredEconomicData(
        ticker="ECBASSETSW",
        name="European Central Bank (ECB) Balance Sheet",
        currency="EUR",
        unit="Millions",
    ),
    "JPNASSETS": FredEconomicData(
        ticker="JPNASSETS",
        name="Bank of Japan (BoJ) Balance Sheet",
        currency="JPY",
        unit="100 Million",
    ),
}


def get_asset_catalog(
    asset_type: Optional[AssetTypes] = None,
) -> dict[str, Metadata]:
    """Returns catalog of assets of the specified type."""
    if asset_type:
        return {k: v for k, v in ALL_DATA.items() if v.type == asset_type}
    return ALL_DATA


def get_symbol_metadata(symbol: str) -> Metadata:
    if symbol not in ALL_DATA:
        raise ValueError(f"missing definition for: {symbol}")
    return ALL_DATA[symbol]
