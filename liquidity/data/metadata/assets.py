from datetime import datetime
from typing import Optional

from liquidity.data.metadata.entities import AssetMetadata, AssetTypes

ALL_ASSETS = {
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
    "UST_10Y": AssetMetadata(
        ticker="UST_10Y",
        name="Interest Rate On 10-Year US Treasury",
        type=AssetTypes.Treasury,
        subtype="Yield",
        maturity="10year",
    ),
    "SPX": AssetMetadata(
        ticker="SPX", name="S&P 500", type=AssetTypes.Index, subtype="Stocks"
    ),
    "NDX": AssetMetadata(
        ticker="NDX", name="Nasdaq-100", type=AssetTypes.Index, subtype="Stocks"
    ),
    "BTC": AssetMetadata(
        ticker="BTC/USD",
        name="Bitcoin",
        currency="USD",
        type=AssetTypes.Crypto,
        subtype="Spot",
    ),
    "ETH": AssetMetadata(
        ticker="ETH/USD",
        name="Ethereum",
        currency="USD",
        type=AssetTypes.Crypto,
        subtype="Spot",
    ),
}


def get_asset_catalog(
    asset_type: Optional[AssetTypes] = None,
) -> dict[str, AssetMetadata]:
    """Returns catalog of assets of the specified type."""
    if asset_type:
        return {k: v for k, v in ALL_ASSETS.items() if v.type == asset_type}
    return ALL_ASSETS


def get_ticker_metadata(ticker: str) -> AssetMetadata:
    if ticker not in ALL_ASSETS:
        raise ValueError(f"missing definition for: {ticker}")
    return ALL_ASSETS[ticker]
