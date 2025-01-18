from functools import cached_property

from liquidity.compute.ticker import Ticker
from liquidity.data.metadata.fields import Fields
from liquidity.visuals.chart import Chart


class PriceRatio:
    """
    Computes and visualizes the price ratio between two financial instruments.

    The price ratio represents the relative price relationship between a primary
    financial instrument (`ticker`) and a benchmark (`benchmark`). This class
    provides functionality to calculate the time series of prices, compute the
    price ratio, and visualize the results using an interactive Plotly line chart.

    Attributes:
    ----------
    ticker : Ticker
        The financial instrument for which the price ratio is calculated.
    benchmark : Ticker
        The benchmark financial instrument used for comparison.

    Methods:
    -------
    df:
        Returns a pandas DataFrame containing the time series of prices for
        both instruments and their computed price ratio.

    show():
        Generates and displays an interactive Plotly chart to visualize
        the price ratio over time.

    Examples:
    --------
    Calculate and visualize the price ratio between two assets:

    >>> ratio = PriceRatio("ETH", "BTC")
    >>> ratio.df
                           CloseETH  CloseBTC  PriceRatio
    Date
    2023-01-01          1400.50     18000.25    0.0778
    2023-01-02          1350.25     17500.50    0.0771
    2023-01-03          1425.00     18500.00    0.0770

    >>> ratio.show()  # Display an interactive chart visualizing the price ratio.

    Visualizing the price ratio with the default benchmark (e.g., SPY):

    >>> ratio = PriceRatio("AAPL")
    >>> ratio.df.head()
                           CloseAAPL  CloseSPY  PriceRatio
    Date
    2023-01-01          145.00      400.00     0.3625
    2023-01-02          150.00      405.00     0.3704
    ...

    >>> ratio.show()
    """

    def __init__(self, ticker: str, benchmark: str = "SPY"):
        self.ticker = Ticker.from_name(ticker)
        self.benchmark = Ticker.from_name(benchmark)

    @cached_property
    def df(self):
        """Returns a pandas DataFrame containing the time series of prices
        for both instruments and their computed ratio.
        """
        ticker = self.ticker.prices.dropna()
        benchmark = self.benchmark.prices.dropna()

        prices = (
            ticker.join(
                benchmark,
                lsuffix=self.ticker.name,
                rsuffix=self.benchmark.name,
            )
            .ffill()
            .dropna()
        )

        def ratio_formula(row):
            return row[f"Close{self.ticker.name}"] / row[f"Close{self.benchmark.name}"]

        prices[Fields.Ratio.value] = prices.apply(ratio_formula, axis=1)
        return prices

    def show(self):
        """
        Generates and displays a chart visualizing the price ratio over time.

        Parameters:
        ----------
        show_all_series : bool, optional
            If True, includes all available time series in the chart (default is False,
            which displays only the yield spread).
        """
        chart_title = f"{self.ticker.name}/{self.benchmark.name} Price Ratio"
        main_series = Fields.Ratio.value

        chart = Chart(
            data=self.df,
            title=chart_title,
            main_series=main_series,
            yaxis_name="Price Ratio",
            xaxis_name="Date",
        )
        chart.show()


if __name__ == "__main__":
    ratio = PriceRatio("ETH", "BTC")
    print(ratio.df.head())

    ratio.show()
