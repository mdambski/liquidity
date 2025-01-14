import plotly.graph_objects as go

from liquidity.compute.ticker import Ticker
from liquidity.data.metadata.fields import Fields


class YieldSpread:
    def __init__(self, ticker: str, ticker_benchmark: str = "TNX"):
        self.ticker = Ticker(ticker)
        self.benchmark = Ticker(ticker_benchmark)

    def get_yields(self):
        ticker = self.ticker.yields.dropna()
        benchmark = self.benchmark.yields.dropna()

        yields = (
            ticker.join(
                benchmark,
                on=Fields.Date.value,
                lsuffix=self.ticker.name,
                rsuffix=self.benchmark.name,
            )
            .ffill()
            .dropna()
        )

        t_yield = f"{Fields.Yield}{self.ticker.name}"
        b_yield = f"{Fields.Yield}{self.benchmark.name}"

        def spread_formula(row):
            return row[t_yield] - row[b_yield]

        yields[Fields.Spread] = yields.apply(spread_formula, axis=1)
        return yields

    def show(self):
        yields = self.get_yields()

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=yields.index,
                y=yields[Fields.Spread],
                mode="lines",
                name="Yield Spread",
                line=dict(color="cadetblue", width=2, dash="solid"),
            )
        )

        # Set chart title and layout
        fig.update_layout(
            title=f"{self.ticker.name} - {self.benchmark.name} Yield Spread",
            title_font=dict(size=20, family="Arial, sans-serif", color="black"),
            xaxis_title="Date",
            yaxis_title="Difference in Percentage Points",
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
            plot_bgcolor="white",  # Clean white background
            paper_bgcolor="ghostwhite",  # Light gray paper background
            hovermode="closest",  # Hover on nearest data point
            font=dict(family="Arial, sans-serif", size=14, color="black"),
        )

        # Show the plot
        fig.show()


if __name__ == "__main__":
    YieldSpread("HYG", "LQD").show()
