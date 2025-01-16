import random
from typing import List, Optional

import pandas as pd
import plotly.graph_objects as go


class Chart:
    """
    A class to generate and display interactive Plotly charts with a primary series
    and optional secondary series in the background.

    Attributes:
        data (pd.DataFrame): DataFrame containing the data to be plotted.
        title (str): Title of the chart.
        main_series (str): The primary series to highlight in the chart.
        secondary_series (Optional[List[str]]): Additional series to show as background.
        yaxis_name (str): Label for the Y-axis.
        xaxis_name (str): Label for the X-axis.
        secondary_colors (List[str]): Palette of colors for secondary series.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        title: str,
        main_series: str,
        secondary_series: Optional[List[str]] = None,
        yaxis_name: str = "Value",
        xaxis_name: str = "Date",
    ):
        self.data = data
        self.title = title
        self.main_series = main_series
        self.secondary_series = secondary_series or []
        self.yaxis_name = yaxis_name
        self.xaxis_name = xaxis_name
        self.secondary_colors = [
            "teal",
            "orange",
            "maroon",
            "gray",
            "lavender",
            "khaki",
            "thistle",
            "plum",
        ]

    def _get_random_color(self, exclude: set) -> str:
        """Select a random color from the palette, excluding already used colors."""
        available_colors = [c for c in self.secondary_colors if c not in exclude]
        return random.choice(available_colors) if available_colors else "gray"

    def _add_main_series(self, fig: go.Figure) -> None:
        """Add the main series to the figure."""
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data[self.main_series],
                mode="lines",
                name=self.main_series,
                line=dict(color="cadetblue", width=3, dash="solid"),
            )
        )

    def _add_secondary_series(self, fig: go.Figure) -> None:
        """Add secondary series to the figure."""
        used_colors = set()
        for series in self.secondary_series:
            if series not in self.data.columns:
                continue

            color = self._get_random_color(used_colors)

            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data[series],
                    mode="lines",
                    name=series,
                    line=dict(color=color, width=2, dash="dot"),
                    opacity=0.7,
                )
            )

            used_colors.add(color)

    def _configure_layout(self, fig: go.Figure) -> None:
        """Configure the layout of the figure."""
        fig.update_layout(
            title=self.title,
            title_font=dict(size=20, family="Arial, sans-serif", color="black"),
            xaxis_title=self.xaxis_name,
            yaxis_title=self.yaxis_name,
            xaxis=dict(
                showgrid=True,
                zeroline=False,
                tickformat="%b %d, %Y",
                tickangle=45,
                gridcolor="whitesmoke",
            ),
            yaxis=dict(
                showgrid=True, zeroline=True, gridcolor="whitesmoke", tickformat=".2f"
            ),
            plot_bgcolor="white",
            paper_bgcolor="ghostwhite",
            hovermode="closest",
            font=dict(family="Arial, sans-serif", size=14, color="black"),
        )

    def show(self) -> None:
        """Generate and display the chart."""
        fig = go.Figure()
        self._add_main_series(fig)
        self._add_secondary_series(fig)
        self._configure_layout(fig)
        fig.show()
