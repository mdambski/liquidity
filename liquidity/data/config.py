from liquidity.data.metadata.entities import AssetMetadata, AssetTypes
from liquidity.data.providers.alpaca_markets import AlpacaCryptoDataProvider
from liquidity.data.providers.alpha_vantage import AlphaVantageDataProvider
from liquidity.data.providers.base import DataProviderBase


def get_data_provider(metadata: AssetMetadata) -> DataProviderBase:
    """Returns data provider for the ticker."""
    if metadata.type == AssetTypes.Crypto:
        return AlpacaCryptoDataProvider()
    return AlphaVantageDataProvider()
