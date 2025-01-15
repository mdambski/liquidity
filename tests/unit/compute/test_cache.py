import tempfile
import uuid

import pandas as pd
import pytest

from liquidity.compute.cache import InMemoryCacheWithPersistence
from liquidity.data.metadata.fields import Fields


@pytest.fixture
def cache_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def cache(cache_dir):
    return InMemoryCacheWithPersistence(cache_dir)


def generate_cache_key():
    return str(uuid.uuid4())


class TestInMemoryCache:
    @pytest.fixture
    def div_data(self):
        return pd.DataFrame(
            {
                Fields.Dividends: [0.5, 0.6, 0.7],
            },
            index=pd.DatetimeIndex(
                data=pd.to_datetime(["2025-02-01", "2025-01-01", "2025-03-01"]),
                name="Date",
            ),
        )

    def test_cache_and_retrieve(self, cache, div_data):
        cache_key = generate_cache_key()

        cache[cache_key] = div_data
        loaded_df = cache[cache_key]

        pd.testing.assert_frame_equal(div_data, loaded_df)

    def test_cache_miss_and_load_from_file(self, cache, cache_dir, div_data):
        cache_key = generate_cache_key()

        # Set cache key, it should also persist it to disk
        cache[cache_key] = div_data

        # Initialize new cache and simulate cache miss
        new_cache = InMemoryCacheWithPersistence(cache_dir)
        loaded_df = new_cache[cache_key]  # on cache-miss should load from disk

        pd.testing.assert_frame_equal(div_data, loaded_df)
