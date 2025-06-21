import json
import os
import random

import pandas as pd
import pytest

from liquidity.visuals import Chart


@pytest.fixture
def generate_fixture(request):
    return request.config.getoption("--generate-fixture")


@pytest.fixture
def chart_data():
    data = pd.DataFrame(
        {
            "Date": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "MainSeries": [10, 12, 13, 14, 17],
            "Secondary1": [5, 4, 3, 2.5, 1.9],
            "Secondary2": [12, 13.5, 13.4, 12.3, 12.1],
        }
    )
    return data.set_index("Date")


@pytest.fixture
def generated_chart(chart_data):
    random.seed(1)  # Ensure reproducibility
    chart = Chart(
        data=chart_data,
        title="Test Chart",
        main_series="MainSeries",
        secondary_series=["Secondary1", "Secondary2"],
    )
    return json.loads(chart.generate_figure().to_json())


@pytest.fixture
def chart_json_path(unittest_fixtures_dir):
    return os.path.join(unittest_fixtures_dir, "chart.json")


@pytest.fixture
def expected_chart_json(chart_json_path, generate_fixture, generated_chart):
    """
    Fixture to load the expected chart JSON or generate it based on a runtime parameter.
    """
    if generate_fixture:
        with open(chart_json_path, "w") as f:
            json.dump(generated_chart, f, indent=4)
        pytest.fail("Fixture generated. Rerun the test without --generate-fixture.")

    # Load the existing fixture
    with open(chart_json_path, "r") as f:
        return json.load(f)


def test_generated_figure_matches_json(expected_chart_json, generated_chart):
    """
    Test that the generated chart matches the expected JSON fixture.

    If changes are made to the `Chart` class or related libraries that affect
    the chart's rendering, the test may fail because the generated chart does
    not match the fixture. Follow these steps to regenerate the fixture and
    compare the new output:

    ## Regenerating the Fixture:

    1. Make changes to the `Chart` class or related libraries.
    2. Regenerate the fixture by running:

        ```
        pytest --generate-fixture
        ```

        This will overwrite the existing `chart.json` with the new chart data.

    Afterward, run `pytest` to confirm the generated chart matches the new fixture.
    """
    assert generated_chart == expected_chart_json, "Generated figure does not match expected JSON"
