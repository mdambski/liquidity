import math
from collections.abc import Iterable
from datetime import datetime
from typing import Optional, Protocol, Tuple

import pandas as pd
import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots  # type: ignore

from liquidity.visuals.chart import Chart


class ChartableModel(Protocol):
    def get_chart(self) -> Chart:
        """Returns a Chart object representing the model's data visualization."""
        ...


class ChartMatrix:
    """
    A class to display liquidity proxies in a 2x2 grid of charts.
    """

    def __init__(
        self,
        models: Iterable[ChartableModel],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ):
        """
        Initialize the LiquidityProxies object.

        If no `start_date` or `end_date` are provided, all available data will be used
        for the charts. This may result in different time ranges for each chart,
        depending on the data available for each model.

        Args:
            start_date (datetime, optional): The start date of the time window for the
                                              chart. If not provided, the earliest
                                              available data is used.
            end_date (datetime, optional): The end date of the time window for the
                                            chart. If not provided, the latest
                                            available data is used.
        """
        self.charts = [model.get_chart() for model in models]
        self.start_date = start_date
        self.end_date = end_date

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

    def get_chart_dimensions(self) -> Tuple[int, int]:
        charts_num = len(self.charts)
        cols = math.isqrt(charts_num)

        if cols**2 == charts_num:
            return cols, cols

        cols += 1
        rows, remainder = divmod(charts_num, cols)

        if remainder > 0:
            rows += 1

        return rows, cols

    def add_chart_to_subplot(self, fig: go.Figure, chart: Chart, row: int, col: int) -> None:
        """
        Add a chart's main series to a subplot.

        Args:
            fig (go.Figure): Plotly figure object to update.
            chart (Chart): Chart object containing data and configuration.
            row (int): Row number of the subplot.
            col (int): Column number of the subplot.
        """
        filtered_data = self.filter_data(chart.data)
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

    def show(self) -> None:
        """
        Display four charts in a grid using Plotly.

        Args:
            charts (List[Chart]): List of Chart objects to display.
            yaxis_names (List[str]): Y-axis labels for each subplot.
            xaxis_name (str): X-axis label for all subplots (default: "Date").
        """
        rows, cols = self.get_chart_dimensions()

        # Create a matrix subplot layout
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=[chart.title for chart in self.charts],
            shared_xaxes=False,
            shared_yaxes=False,
            horizontal_spacing=0.1,
            vertical_spacing=0.15,
        )

        # Add each chart to the appropriate subplot
        for idx, chart in enumerate(self.charts):
            row, col = divmod(idx, cols)
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
