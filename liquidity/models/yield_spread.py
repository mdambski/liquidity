from matplotlib import pyplot as plt

from liquidity.compute.ticker import Ticker
from liquidity.data.metadata.fields import Fields


class YieldSpread:
    def __init__(self, ticker: str, ticker_benchmark: str = "TNX"):
        self.ticker = Ticker(ticker)
        self.benchmark = Ticker(ticker_benchmark)

    def get_yields(self):
        yields = (
            self.ticker.yields.join(
                self.benchmark.yields,
                on=Fields.Date,
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
        yields[[Fields.Spread]].plot(
            figsize=(10, 6),
            title=f"{self.ticker.name} - {self.benchmark.name} Yield spread",
        )
        plt.show()


if __name__ == "__main__":
    YieldSpread("HYG", "UST_10Y").show()
