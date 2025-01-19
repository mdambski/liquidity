# Market Liquidity Proxies

This repository provides an overview of key market liquidity proxies and additional alternatives for crypto, bond, and stock markets. These proxies serve as indicators of market sentiment, risk appetite, and liquidity conditions.

---

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

**Retrieve API Key**: Go to the [Alphavantage.co](https://www.alphavantage.co/) website and retrieve free api-key. Set the api-key as an environment variable.
```bash
export ALPHAVANTAGE_API_KEY="<your-api-key>"
```

## Usage
Here is example usage using python code, to display matrix chart with liquidity proxies:

```python
from liquidity.models import YieldSpread, PriceRatio
from liquidity.visuals import ChartMatrix, Chart


liquidity_proxies = ChartMatrix(years=5)

# Define the data sources and charts
charts = [
    Chart(
        data=YieldSpread("HYG", "LQD").df,
        title="HYG - LQD Yield Spread",
        main_series="Spread",
        yaxis_name="Yield spread",
    ),
    Chart(
        data=YieldSpread("LQD", "UST-10Y").df,
        title="LQD - UST10Y Yield Spread",
        main_series="Spread",
        yaxis_name="Yield spread",
    ),
    Chart(
        data=PriceRatio("QQQ", "SPY").df,
        title="QQQ/SPY Price Ratio",
        main_series="Ratio",
        yaxis_name="Price ratio",
    ),
    Chart(
        data=PriceRatio("ETH", "BTC").df,
        title="ETH/BTC Price Ratio",
        main_series="Ratio",
        yaxis_name="Price ratio",
    ),
]

# Display the matrix grid of charts
liquidity_proxies.display_matrix(charts)
```


This will display example chart:
![Liquidity proxies](examples/liquidity-proxies.png)


## Data Sources

This repository is based on market data APIs providing free access to data.

- **Cryptocurrency Prices**: [Alpaca.markets](https://alpaca.markets/)
- **Other Market Data**: [Alphavantage.co](https://www.alphavantage.co/)


## Future Improvements
In the future I plan to add even more data providers and liquidity proxies.
