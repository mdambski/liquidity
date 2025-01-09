import os
from unittest.mock import patch

import pytest
from liquidity.data.providers.alpha_vantage import (
    AlphaVantageConfig,
    AlphaVantageDataProvider,
)


@pytest.fixture
def config():
    config = AlphaVantageConfig()
    config.api_key = "fake-api-key"
    yield config


@pytest.fixture
def config_env(config):
    with patch.dict(os.environ, {"ALPHAVANTAGE_API_KEY": config.api_key}):
        yield AlphaVantageConfig()


def test_envvars_set_config_values(config_env, config):
    assert config.model_dump() == config_env.model_dump()


def test_apikey_empty_by_default():
    with patch.dict(os.environ, clear=True):
        provider = AlphaVantageDataProvider()
        assert provider.api_key is None
