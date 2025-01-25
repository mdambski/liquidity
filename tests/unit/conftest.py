import os

import pytest


def pytest_addoption(parser):
    """Add a custom command-line option to pytest."""
    parser.addoption(
        "--generate-fixture",
        action="store_true",
        default=False,
        help="Generate and save the JSON fixture instead of running the test",
    )


@pytest.fixture
def unittest_fixtures_dir():
    return os.path.join(os.path.dirname(__file__), "fixtures")
