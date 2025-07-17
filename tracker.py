class PriceTracker:
    """Track last seen prices for contract identifiers."""

    def __init__(self):
        self.last_prices: dict[str, float] = {}

    def update_and_get_change(self, contract: str, price: float) -> float:
        """Update price for ``contract`` and return percent change.

        If ``contract`` has not been seen before, store ``price`` and return
        0.0.
        """
        previous = self.last_prices.get(contract)
        self.last_prices[contract] = price
        if previous is None or previous == 0:
            return 0.0
        return (price - previous) / previous * 100
