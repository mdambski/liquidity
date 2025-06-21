from datetime import datetime
from typing import Optional

import pandas as pd
import plotly.graph_objects as go  # type: ignore

from liquidity.data.metadata.assets import get_symbol_metadata
from liquidity.data.metadata.entities import FredEconomicData
from liquidity.data.providers.fred import FredEconomicDataProvider


class GlobalLiquidity:
    """
    The Global Liquidity model computes a combined net liquidity index based on key economic indicators from the FRED database.

    Data Series:
    1. US Federal Reserve Balance Sheet (WALCL):
       - Measures the total assets on the Fed's balance sheet.
       - Impact: Positive. Increases in Fed assets (e.g., through asset purchases) inject liquidity into the system.

    2. Reserve Balances with Federal Reserve Banks (WRESBAL):
       - Total reserves held by commercial banks at the Fed.
       - Impact: Positive. Higher reserve balances indicate more available liquidity for lending and economic activity.

    3. Overnight Reverse Repurchase Agreements (RRPONTSYD):
       - Represents short-term sales of securities by the Fed with an agreement to repurchase them.
       - Impact: Negative. Reverse repos drain liquidity from the system by temporarily absorbing money.

    4. U.S. Treasury General Account (WTREGEN):
       - The government's account at the Fed used for daily operations.
       - Impact: Negative. Increases in the TGA reduce liquidity in the financial system as funds are absorbed by the government.

    Model Description:
    The liquidity index is computed by summing the contributions of the above components, with positive impacts added and negative impacts subtracted. All data is standardized to billions of USD.

    Visualization:
    The model includes a stacked area chart showing the individual contributions of each series and the combined liquidity index. The main liquidity index is plotted in red and with a thicker line for clarity.
    """

    SERIES_MAPPING = {
        "ECB Balance Sheet": ("ECBASSETSW", 1),  # Positive impact on liquidity
        "Fed Balance Sheet": ("WALCL", 1),  # Positive impact on liquidity
        "Reserve Balances": ("WRESBAL", 1),  # Positive impact on liquidity
        "Reverse Repo": ("RRPONTSYD", -1),  # Negative impact (liquidity drain)
        "Treasury General Account": (
            "WTREGEN",
            -1,
        ),  # Negative impact (liquidity drain)
    }

    def __init__(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        self.provider = FredEconomicDataProvider()
        self.start_date = start_date
        self.end_date = end_date
        self.data = self._fetch_data()

    def filter_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Filter the DataFrame to include only the desired time period.

        Args:
            data (pd.DataFrame): DataFrame with a DateTimeIndex.

        Returns:
            pd.DataFrame: Filtered DataFrame with rows for desired time frame.
        """
        assert isinstance(data.index, pd.DatetimeIndex)

        start_date = pd.Timestamp(self.start_date or data.index[0])
        end_date = pd.Timestamp(self.end_date or data.index[-1])

        return data.loc[start_date:end_date]  # type: ignore[misc]

    def _fetch_data(self) -> pd.DataFrame:
        """Fetch all required data series and return a combined DataFrame."""
        dfs = []

        for name, (ticker, sign) in self.SERIES_MAPPING.items():
            df = self.provider.get_data(ticker)

            # Get metadata to check unit
            metadata = get_symbol_metadata(ticker)
            df.rename(columns={"Close": name}, inplace=True)

            df = self.ensure_consistent_unit(df, metadata)

            # Apply sign to reflect liquidity impact
            df *= sign

            dfs.append(self.filter_data(df))

        # Merge all data on the date index
        combined_df = pd.concat(dfs, axis=1).ffill().dropna()

        return combined_df

    def convert_currency(
        self, df: pd.DataFrame, currency_from: str, currency_to: str
    ) -> pd.DataFrame:
        """Convert currency from original currency like JPY, EUR to desired currency like USD,
        to ensure the comparison is consistent. Currency conversions are executed using the
        exchange course retrieved from FRED Economic database.
        """
        if currency_from == currency_to:
            return df

        # This is mapping with supported currency conversions.
        # The mapping uses FRED series, the format of the mapping:
        # Dict[(currency_from, currency_to), fred_series]
        conversions_map = {("USD", "EUR"): "DEXUSEU", ("JPY", "USD"): "DEXJPUS"}

        key = (currency_from, currency_to)
        inv = (currency_to, currency_from)

        if key in conversions_map:
            fred_series = conversions_map[key]
            exchange_rate = self.provider.get_data(fred_series)

        elif inv in conversions_map:
            fred_series = conversions_map[inv]
            exchange_rate = self.provider.get_data(fred_series)
            exchange_rate = 1 / exchange_rate

        else:
            raise ValueError("Unsupported currency pair")

        def convert_currency(row):
            return row["ECB Balance Sheet"] * row["Close"]

        df = pd.concat([df, exchange_rate.ffill()], axis=1).dropna()

        return pd.DataFrame(
            data={"ECB Balance Sheet": df.apply(convert_currency, axis=1)},
            index=df.index,
        )

    def convert_unit(self, df: pd.DataFrame, unit: str) -> pd.DataFrame:
        coefficient = {"Millions": 0.001, "Billions": 1, "Trillions": 1000}[unit]

        if coefficient != 1:
            df *= coefficient

        return df

    def ensure_consistent_unit(self, df: pd.DataFrame, metadata: FredEconomicData) -> pd.DataFrame:
        df = self.convert_currency(df, currency_from=metadata.currency, currency_to="USD")
        df = self.convert_unit(df, unit=metadata.unit)
        return df

    @property
    def liquidity_index(self) -> pd.DataFrame:
        """Compute the net liquidity index by summing all series."""
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
