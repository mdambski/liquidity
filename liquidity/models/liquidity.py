from datetime import datetime
from typing import Dict, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go  # type: ignore

from liquidity.data.metadata.assets import get_symbol_metadata
from liquidity.data.metadata.entities import FredEconomicData
from liquidity.data.providers.fred import FredEconomicDataProvider


class GlobalLiquidity:
    """
    The Global Liquidity model estimates net financial system liquidity using key
    macroeconomic indicators from the FRED database. It captures how central banks and fiscal
    authorities inject or withdraw liquidity from markets.

    Notes
    -----
    The liquidity index aggregates the effects of:

    1. US Federal Reserve Balance Sheet (WALCL):
       - Measures the total assets on the Fed's balance sheet.
       - Impact: Positive. Increases in Fed assets (e.g., through asset purchases) inject
         liquidity into the system.

    2. Reserve Balances with Federal Reserve Banks (WRESBAL):
       - Total reserves held by commercial banks at the Fed.
       - Impact: Positive. Higher reserve balances indicate more available liquidity for
         lending and economic activity.

    3. Overnight Reverse Repurchase Agreements (RRPONTSYD):
       - Represents short-term sales of securities by the Fed with an agreement to repurchase
         them.
       - Impact: Negative. Reverse repos drain liquidity from the system by temporarily
         absorbing money.

    4. U.S. Treasury General Account (WTREGEN):
       - The government's account at the Fed used for daily operations.
       - Impact: Negative. Increases in the TGA reduce liquidity in the financial system as
         funds are absorbed by the government.

    5. ECB Balance Sheet (ECBASSETSW):
       - Measures total assets held by the European Central Bank.
       - Impact: Positive. ECB asset purchases contribute to global liquidity flows.

    Model Description:
    The liquidity index is computed by summing the contributions of the above components,
    with positive impacts added and negative impacts subtracted. All values are standardized
    to billions of USD.

    Visualization:
    The model displays a stacked area chart showing the individual contributions of each
    series, with the overall liquidity index overlaid in bold for clarity.

    Examples
    --------
    >>> model = GlobalLiquidity(start_date=datetime(2020, 1, 1))
    >>> model.show()
    """

    SERIES_MAPPING: Dict[str, Tuple[str, int]] = {
        "ECB Balance Sheet": ("ECBASSETSW", 1),
        "Fed Balance Sheet": ("WALCL", 1),
        "Reserve Balances": ("WRESBAL", 1),
        "Reverse Repo": ("RRPONTSYD", -1),
        "Treasury General Account": ("WTREGEN", -1),
    }

    CURRENCY_CONVERSIONS = {
        ("USD", "EUR"): "DEXUSEU",
        ("JPY", "USD"): "DEXJPUS",
    }

    UNIT_CONVERSION_FACTORS = {
        "Millions": 1e-3,
        "Billions": 1,
        "Trillions": 1e3,
    }

    def __init__(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        self.provider = FredEconomicDataProvider()
        self.start_date = pd.Timestamp(start_date) if start_date else None
        self.end_date = pd.Timestamp(end_date) if end_date else None
        self.data = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """
        Fetches and processes all configured FRED data series.
        Returns:
            pd.DataFrame: Combined, signed, and standardized data.
        """
        processed_series = []

        for name, (ticker, sign) in self.SERIES_MAPPING.items():
            df = self.provider.get_data(ticker).rename(columns={"Close": name})
            metadata = self._validate_and_get_metadata(ticker)
            df = self._standardize_series(df, name, metadata)
            df[name] *= sign
            processed_series.append(self._filter_date_range(df))

        combined = pd.concat(processed_series, axis=1).ffill().dropna()
        return combined

    def _validate_and_get_metadata(self, ticker: str) -> FredEconomicData:
        metadata = get_symbol_metadata(ticker)
        if not isinstance(metadata, FredEconomicData):
            raise ValueError(f"Expected FredEconomicData, got {type(metadata)} for {ticker}")
        return metadata

    def _standardize_series(
        self, df: pd.DataFrame, column: str, metadata: FredEconomicData
    ) -> pd.DataFrame:
        df = self._convert_currency(df, column, metadata.currency, "USD")
        df[column] *= self.UNIT_CONVERSION_FACTORS.get(metadata.unit, 1)
        return df

    def _convert_currency(
        self, df: pd.DataFrame, column: str, currency_from: str, currency_to: str
    ) -> pd.DataFrame:
        if currency_from == currency_to:
            return df

        # Check direct or inverse conversion series
        pair = (currency_from, currency_to)
        inverse_pair = (currency_to, currency_from)

        if pair in self.CURRENCY_CONVERSIONS:
            fx_series = self.provider.get_data(self.CURRENCY_CONVERSIONS[pair])
            fx_rate = fx_series["Close"]
        elif inverse_pair in self.CURRENCY_CONVERSIONS:
            fx_series = self.provider.get_data(self.CURRENCY_CONVERSIONS[inverse_pair])
            fx_rate = 1 / fx_series["Close"]
        else:
            raise ValueError(
                f"Currency conversion from {currency_from} to {currency_to} not supported"
            )

        # Align and multiply with FX rate
        df = df.copy()
        df["fx"] = fx_rate.ffill()
        df[column] = df[column] / df["fx"]
        return df.drop(columns="fx")

    def _filter_date_range(self, df: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame index must be a DatetimeIndex")

        start = self.start_date or df.index.min()
        end = self.end_date or df.index.max()
        return df.loc[start:end]  # type: ignore[misc]

    @property
    def liquidity_index(self) -> pd.DataFrame:
        """
        Computes the total net liquidity index.
        Returns:
            pd.DataFrame: Original series + computed 'Liquidity Index' column.
        """
        df = self.data.copy()
        df["Liquidity Index"] = df.sum(axis=1)
        return df

    def show(self):
        """Plot stacked area chart of liquidity components along with
        the combined liquidity index.
        """
        df = self.liquidity_index

        fig = go.Figure()

        # Stacked area chart for components
        for column in self.SERIES_MAPPING.keys():
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[column],
                    mode="lines",
                    stackgroup="one",
                    name=column,
                    line=dict(width=0.5),
                )
            )

        # Main liquidity index with red color and thicker line
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Liquidity Index"],
                mode="lines",
                name="Liquidity Index",
                line=dict(width=3, color="black"),
            )
        )

        # Update layout with title and axis labels
        fig.update_layout(
            title="Global Liquidity Components & Total Liquidity Index",
            xaxis_title="Date",
            yaxis_title="Liquidity Value (Billions of USD)",
            template="plotly_white",
            hovermode="x",
            showlegend=True,
        )

        fig.show()
