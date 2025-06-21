# Market Liquidity Proxies

This repository provides an overview of key market liquidity proxies and additional alternatives for crypto, bond, and stock markets. These proxies serve as indicators of market sentiment, risk appetite, and liquidity conditions.

---

## Global Liquidity Model

This module generates a chart of the **Global Liquidity Model** using data from FRED, the Federal Reserve, the U.S. Treasury, and other central banks. It estimates global liquidity based on publicly available macroeconomic indicators.


## Proxies Overview

### Crypto Proxies

1. **Ethereum / Bitcoin (ETH / BTC)**:
Reflects liquidity preference and risk sentiment within the cryptocurrency market. Barring idiosyncratic events it acts as a proxy for broader market liquidity.

### Stock Market ETF Ratios
2. **QQQ / SPY Ratio**:
Reflects liquidity preference and risk sentiment within the US stock market. Shows the performance of high-beta QQQ (Nasdaq-100) vs. SPY (S&P 500).

### Bond Market ETF Yield Spreads
Reflect funding stress in the broader market. When liquidity is ample, spreads tend to be tight, and they widen when liquidity is drained and stress builds in the system.

3. **HYG / LQD Spread**:
Measures the risk premium between high-yield (HYG) and investment-grade bonds (LQD).

4. **LQD / TNX Spread**:
Measures the risk premium between investment-grade bonds (LQD) and 10-year Treasury yields (UST-10Y).


## Installation

**Install package from PyPi**:
In order to install package use package manager of your choice, the most standard command is:
```bash
pip install liquidity
```

**Retrieve API Key**: Depending on what charts/models you want to generate you will need corresponding key:
- For FRED Economic database request the key from FRED. [Here are instructions](https://fred.stlouisfed.org/docs/api/api_key.html).
- For crypto go to the [Alphavantage.co](https://www.alphavantage.co/) website and retrieve free api-key.

Set the api-key as an environment variable.
```bash
export FRED_API_KEY="<your-api-key>"
export ALPHAVANTAGE_API_KEY="<your-api-key>"
```

## Usage
Below are some example code snippets:

#### Generate the Full Model

**Example 1: Generate liquidity model**

To generate the model using all available data:

```python
from liquidity.models.liquidity import GlobalLiquidity

model = GlobalLiquidity()
model.show()
```

The code will retrieve data using the FRED Economi database API, and generate the liquidity chart. Below example of generated chart:
![Liquidity proxies](examples/global-liquidity-model.png)

To generate the model for a specific date range:

```python
from liquidity.models.liquidity import GlobalLiquidity
from datetime import datetime

model = GlobalLiquidity(
    start_date=datetime(2021, 1, 1),
    end_date=datetime(2024, 12, 31)
)
model.show()
```

Below are code snippets demonstrating how to display multiple charts combined into a single matrix, showcasing various liquidity proxies:
**Example 2: Display a 2x2 Matrix of Charts**
```python
from datetime import datetime
from liquidity.models import YieldSpread, PriceRatio
from liquidity.visuals import ChartMatrix

# Define a ChartMatrix object with 4 models
liquidity_proxies = ChartMatrix(
    models=[
        YieldSpread("HYG", "LQD"),
        YieldSpread("LQD", "UST-10Y"),
        PriceRatio("QQQ", "SPY"),
        PriceRatio("ETH", "BTC"),
    ],
    start_date=datetime(2020, 1, 1),
)

# Display the matrix grid of charts
liquidity_proxies.show()
```

This code will retrieve data from the available API providers for each of the specified liquidity proxies and display them in a 2x2 matrix chart. The charts will cover the period starting from January 1, 2020. Here's a preview of what the result will look like:
![Liquidity proxies](examples/matrix-chart-2x2-last-five-years.png)


**Example 3: Display a 2x3 Matrix of Charts for a Full Year**
As the number of models increases, the method automatically determines the optimal layout for the matrix grid. For instance, if you have six charts, the layout will adjust accordingly.

Here’s an example of displaying a 2x3 matrix for the year 2024:
```python
from datetime import datetime
from liquidity.models import YieldSpread, PriceRatio
from liquidity.visuals import ChartMatrix

# Define a ChartMatrix object with 6 models
liquidity_proxies = ChartMatrix(
    models=[
        YieldSpread("HYG", "LQD"),
        YieldSpread("HYG", "UST-10Y"),
        YieldSpread("LQD", "UST-10Y"),
        PriceRatio("QQQ", "SPY"),
        PriceRatio("BTC", "QQQ"),
        PriceRatio("ETH", "BTC"),
    ],
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
)

# Display the matrix of charts
liquidity_proxies.show()
```

This example retrieves data for the specified liquidity proxies over the year 2024 and displays the results in a 2x3 matrix. The layout will automatically adjust based on the number of models, ensuring the charts are well-organized and easy to interpret. Here is an example output for the 2024 data:
![Liquidity proxies](examples/matrix-chart-2x3-2024-year.png)

### Notes:
- Optional start_date and end_date Parameters: Both the start_date and end_date parameters are optional. If not specified, the method will use the full available data range for each chart. However, be aware that this may cause the time frames of each chart to differ, as different symbols (e.g., "HYG", "QQQ", "ETH") may have varying lengths of historical data available from the API providers.

- Automatic Layout Adjustment: As the number of models increases, the method will automatically adjust the layout of the matrix to ensure the charts are displayed in a clean, readable format.

- Data Retrieval: The charts will pull data from available API providers once a day (subsequent calss will be loaded from cache) for the specified models, ensuring accurate and up-to-date information.

- Custom Date Ranges: If you want to focus on specific time periods, you can provide both start_date and end_date. Otherwise, the method will display data for the full available range.

## Data Sources

This repository is based on market data APIs providing free access to data.

- **Cryptocurrency Prices**: [Alpaca.markets](https://alpaca.markets/)
- **FRED Economic Database**: [FRED](https://www.stlouisfed.org/)
- **Other Market Data**: [Alphavantage.co](https://www.alphavantage.co/)


## Future Improvements
In the future I plan to add even more data providers and liquidity proxies.
