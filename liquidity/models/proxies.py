from datetime import datetime, timedelta
from typing import List

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from liquidity.compute.chart import Chart
from liquidity.models.price_ratio import PriceRatio
from liquidity.models.yield_spread import YieldSpread


class LiquidityProxies:
    """
    A class to display liquidity proxies in a 2x2 grid of charts.
    """

    def __init__(self, years: int = 5):
        """
        Initialize the LiquidityProxies object.

        Args:
            years (int): The number of years of data to filter (default is 5).
        """
        self.years = years

    def filter_data_last_n_years(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Filter the DataFrame to include only the last `n` years of data.

        Args:
            data (pd.DataFrame): DataFrame with a DateTimeIndex.

        Returns:
            pd.DataFrame: Filtered DataFrame with rows from the last `n` years.
        """
        cutoff_date = datetime.now() - timedelta(days=self.years * 365)
        return data[data.index >= cutoff_date]

    def add_chart_to_subplot(
        self, fig: go.Figure, chart: Chart, row: int, col: int
    ) -> None:
        """
        Add a chart's main series to a subplot.

        Args:
            fig (go.Figure): Plotly figure object to update.
            chart (Chart): Chart object containing data and configuration.
            row (int): Row number of the subplot.
            col (int): Column number of the subplot.
        """
        filtered_data = self.filter_data_last_n_years(chart.data)
        fig.add_trace(
            go.Scatter(
                x=filtered_data.index,
                y=filtered_data[chart.main_series],
                mode="lines",
                name=chart.main_series,
                line=dict(color="cadetblue", width=3, dash="solid"),
            ),
            row=row,
            col=col,
        )

    def display_2x2_matrix(
        self, charts: List[Chart], yaxis_names: List[str], xaxis_name: str = "Date"
    ) -> None:
        """
        Display four charts in a 2x2 grid using Plotly.

        Args:
            charts (List[Chart]): List of Chart objects to display.
            yaxis_names (List[str]): Y-axis labels for each subplot.
            xaxis_name (str): X-axis label for all subplots (default: "Date").
        """
        assert len(charts) == 4, "Exactly four charts are required for a 2x2 grid."

        # Create a 2x2 subplot layout
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=[chart.title for chart in charts],
            shared_xaxes=False,
            shared_yaxes=False,
        )

        # Add each chart to the appropriate subplot
        for idx, chart in enumerate(charts):
            row, col = divmod(idx, 2)
            self.add_chart_to_subplot(fig, chart, row + 1, col + 1)
            fig.update_yaxes(title_text=yaxis_names[idx], row=row + 1, col=col + 1)
            fig.update_xaxes(title_text=xaxis_name, row=row + 1, col=col + 1)

        # Update layout and show the figure
        fig.update_layout(
            title="Liquidity Proxies",
            title_font=dict(size=20, family="Arial, sans-serif", color="black"),
            plot_bgcolor="white",
            paper_bgcolor="ghostwhite",
            font=dict(family="Arial, sans-serif", size=14, color="black"),
        )
        fig.show()


if __name__ == "__main__":
    # Instantiate LiquidityProxies object
    liquidity_proxies = LiquidityProxies(years=5)

    # Define the data sources and charts
    charts = [
        Chart(
            data=YieldSpread("HYG", "LQD").df,
            title="HYG - LQD Yield Spread",
            main_series="Spread",
        ),
        Chart(
            data=YieldSpread("LQD", "UST-10Y").df,
            title="LQD - UST10Y Yield Spread",
            main_series="Spread",
        ),
        Chart(
            data=PriceRatio("QQQ", "SPY").df,
            title="QQQ/SPY Price Ratio",
            main_series="Ratio",
        ),
        Chart(
            data=PriceRatio("ETH", "BTC").df,
            title="ETH/BTC Price Ratio",
            main_series="Ratio",
        ),
    ]

    # Display the 2x2 grid of charts
    liquidity_proxies.display_2x2_matrix(
        charts=charts,
        yaxis_names=["Yield Diff", "Yield Diff", "Price Ratio", "Price Ratio"],
    )
