# Market Liquidity Proxies

This repository provides an overview of key market liquidity proxies and additional alternatives for crypto, bond, and stock markets. These proxies serve as indicators of market sentiment, risk appetite, and liquidity conditions.

---

## Proxies Overview

### Crypto Proxies

1. **Ethereum / Bitcoin (ETH / BTC)**:
Reflects liquidity preference and risk sentiment within the cryptocurrency market. Barring idiosyncratic events it acts as a proxy for broader market liquidity.

### Stock Market ETF Ratios
2. **QQQ / SPY Ratio**:
Reflects liquidity preference and risk sentiment within the US stock market. Shows performance of high beta QQQ (Nasdaq-100) vs SPY (S&P 500).

### Bond Market ETF Yield Spreads
Reflects funding stress in the broader market, with ample liquidity spreads tend to be tight, and widen when liquidity is drained and there is stress in the system.

3**HYG / LQD Spread**:
Measures the risk premium between high-yield (HYG) and investment-grade bonds (LQD).

4**LQD / TNX Spread**:
Measures the risk premium between investment-grade bonds (LQD) and 10-year Treasury yields (UST-10Y).


## Installation

#### Step 1
**Install Poetry (if not already installed):**
You can install Poetry by following the instructions from their [official website](https://python-poetry.org/).
For most systems, you can install it using this command:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Alternatively, for Windows, you might use:
```bash
python -m pip install poetry
```

#### Step 2
**Navigate to the Project Directory**: After downloading the project, open a terminal or command prompt, and navigate to the project directory:
```bash
git clone https://github.com/mdambski/liquidity.git
cd liquidity
```

#### Step 3
**Install the Dependencies**: Run the following command to install all the dependencies specified in pyproject.toml:
```bash
poetry install
```

#### Step 4
**Retrieve API Key**: Go to the [Alphavantage.co](https://www.alphavantage.co/) website and retrieve free api-key.
```bash
export ALPHAVANTAGE_API_KEY="<your-api-key>"
make run
```

This will generate summary of all liquidity proxies:
Example chart displayed:
![Liquidity proxies](liquidity/data/examples/liquidity-proxies.png)


## Data Sources

This repository is based on market data APIs providing free access to data.

- **Cryptocurrency Prices**: [Alpaca.markets](https://alpaca.markets/)
- **Other Market Data**: [Alphavantage.co](https://www.alphavantage.co/)


## Future Improvements
In the future I plan to add even more data providers and liquidity proxies.
When there is enough features I will make a PyPI package to simplify installation.
