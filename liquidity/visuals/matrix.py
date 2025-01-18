import math
from datetime import datetime, timedelta
from typing import List

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from liquidity.models.price_ratio import PriceRatio
from liquidity.models.yield_spread import YieldSpread
from liquidity.visuals.chart import Chart


class ChartMatrix:
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

    def display_matrix(self, charts: List[Chart]) -> None:
        """
        Display four charts in a NxN grid using Plotly.

        Args:
            charts (List[Chart]): List of Chart objects to display.
            yaxis_names (List[str]): Y-axis labels for each subplot.
            xaxis_name (str): X-axis label for all subplots (default: "Date").
        """
        matrix_side = math.isqrt(len(charts))
        assert matrix_side**2 == len(charts), (
            "The number of charts must be a perfect square "
            "(e.g., 4, 9, 16, etc.) to form a square grid for "
            "a matrix chart."
        )

        # Create a matrix subplot layout
        fig = make_subplots(
            rows=matrix_side,
            cols=matrix_side,
            subplot_titles=[chart.title for chart in charts],
            shared_xaxes=False,
            shared_yaxes=False,
            horizontal_spacing=0.1,
            vertical_spacing=0.15,
        )

        # Add each chart to the appropriate subplot
        for idx, chart in enumerate(charts):
            row, col = divmod(idx, matrix_side)
            self.add_chart_to_subplot(fig, chart, row + 1, col + 1)
            fig.update_yaxes(title_text=chart.yaxis_name, row=row + 1, col=col + 1)
            fig.update_xaxes(title_text=chart.xaxis_name, row=row + 1, col=col + 1)

        # Update layout and show the figure
        fig.update_layout(
            title=dict(
                text="Liquidity Proxies",
                font=dict(size=24, family="Helvetica, sans-serif", color="black"),
                x=0.5,  # Center-align the title
                xanchor="center",
            ),
            yaxis_title=dict(
                font=dict(size=16, family="Roboto, sans-serif", color="dimgray"),
            ),
            font=dict(
                family="Roboto, sans-serif",
                size=14,
                color="dimgray",
            ),
            plot_bgcolor="white",
            paper_bgcolor="ghostwhite",
            showlegend=False,
        )
        fig.show()


if __name__ == "__main__":
    # Instantiate LiquidityProxies object
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
