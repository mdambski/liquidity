from liquidity.data.metadata.assets import get_ticker_metadata
from liquidity.data.metadata.entities import AssetTypes
from liquidity.data.providers.alpaca_markets import AlpacaCryptoDataProvider
from liquidity.data.providers.alpha_vantage import AlphaVantageDataProvider
from liquidity.data.providers.base import DataProviderBase


def get_data_provider(ticker: str) -> DataProviderBase:
    """Returns data provider for the ticker."""
    metadata = get_ticker_metadata(ticker)
    if metadata.type == AssetTypes.Crypto:
        return AlpacaCryptoDataProvider()
    return AlphaVantageDataProvider()
