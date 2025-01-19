from functools import cached_property

from liquidity.compute.ticker import Ticker
from liquidity.data.metadata.fields import Fields
from liquidity.visuals import Chart


class YieldSpread:
    """
    Calculate and visualize the yield spread between two financial instruments.

    The yield spread represents the difference in yields (expressed as percentage
    points) between a given financial instrument (ticker) and a benchmark.
    This class provides tools to calculate the time series of yields, compute
    the spread, and visualize the result using an interactive  Plotly line chart.

    Attributes:
    ----------
    ticker : Ticker
        The financial instrument for which the yield spread is calculated.
    benchmark : Ticker
        The benchmark financial instrument used for comparison.

    Methods:
    -------
    df:
        Returns a pandas DataFrame containing the time series of yields
        for both instruments and their computed spread.

    show():
        Generates and displays an interactive Plotly chart to visualize
        the yield spread over time.

    Example:
    --------
    Calculate and visualize the yield spread between HYG (High Yield Corporate Bond ETF)
    and LQD (Investment Grade Corporate Bond ETF):

    >>> spread = YieldSpread("HYG", "LQD")
    >>> spread.df  # Access the computed DataFrame of yields and spread
                          YieldHYG  YieldLQD   Spread
    Date
    2023-01-01           5.50      3.20       2.30
    2023-01-02           5.48      3.25       2.23
    2023-01-03           5.51      3.19       2.32
    ...

    >>> spread.show()  # Display an interactive chart of the yield spread

    Visualizing with the default benchmark (10-year Treasury Note, UST_10Y):

    >>> spread = YieldSpread("HYG")
    >>> spread.show()
    """

    def __init__(self, ticker: str, benchmark: str = "UST-10Y"):
        self.ticker = Ticker.from_name(ticker)
        self.benchmark = Ticker.from_name(benchmark)

    @cached_property
    def df(self):
        """Returns a pandas DataFrame containing the time series of
        yields for both instruments and their computed spread.
        """
        ticker = self.ticker.yields.dropna()
        benchmark = self.benchmark.yields.dropna()

        yields = (
            ticker.join(
                benchmark,
                lsuffix=self.ticker.name,
                rsuffix=self.benchmark.name,
            )
            .ffill()
            .dropna()
        )

        def spread_formula(row):
            return row[f"Yield{self.ticker.name}"] - row[f"Yield{self.benchmark.name}"]

        yields[Fields.Spread.value] = yields.apply(spread_formula, axis=1)
        return yields

    def show(self, show_all_series: bool = False):
        """
        Generates and displays a chart visualizing the yield spread over time.

        Parameters:
        ----------
        show_all_series : bool, optional
            If True, includes all available time series in the chart (default is False,
            which displays only the yield spread).
        """
        chart_title = f"{self.ticker.name} - {self.benchmark.name} Yield Spread"
        main_series = Fields.Spread.value

        secondary_series = None
        if show_all_series:
            secondary_series = [col for col in self.df.columns if col != main_series]

        chart = Chart(
            data=self.df,
            title=chart_title,
            main_series=main_series,
            secondary_series=secondary_series,
            yaxis_name="Yield difference in percentage points",
            xaxis_name="Date",
        )
        chart.show()
