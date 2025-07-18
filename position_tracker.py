class PositionTracker:
    """Track open positions and realized PnL using FIFO cost basis."""

    def __init__(self):
        # per symbol queue of lots [{'qty': float, 'price': float}]
        self.positions: dict[str, list[dict[str, float]]] = {}
        # realized profit in dollars per symbol
        self.realized_pnl: dict[str, float] = {}
        # total cost basis for closed lots per symbol
        self.closed_basis: dict[str, float] = {}

    def add_trade(
        self, symbol: str, qty: float, price: float, side: str
    ) -> None:
        """Record a trade and update FIFO positions.

        Parameters
        ----------
        symbol: str
            The contract identifier.
        qty: float
            Quantity traded.
        price: float
            Trade price.
        side: str
            ``"BUY"`` to open/add, ``"SELL"`` to close.
        """
        side = side.upper()
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")

        queue = self.positions.setdefault(symbol, [])
        if side == "BUY":
            queue.append({"qty": float(qty), "price": float(price)})
            return

        # SELL path - close existing lots using FIFO
        qty_remaining = float(qty)
        while qty_remaining > 0:
            if not queue:
                raise ValueError(
                    f"Attempting to sell more than open quantity for {symbol}"
                )
            lot = queue[0]
            close_qty = min(qty_remaining, lot["qty"])
            lot["qty"] -= close_qty
            if lot["qty"] == 0:
                queue.pop(0)
            pnl = (price - lot["price"]) * close_qty
            self.realized_pnl[symbol] = (
                self.realized_pnl.get(symbol, 0.0) + pnl
            )
            self.closed_basis[symbol] = (
                self.closed_basis.get(symbol, 0.0)
                + lot["price"] * close_qty
            )
            qty_remaining -= close_qty

    def get_open_quantity(self, symbol: str) -> float:
        """Return the remaining open quantity for ``symbol``."""
        queue = self.positions.get(symbol, [])
        return sum(lot["qty"] for lot in queue)

    def calculate_pnl(self, symbol: str) -> float:
        """Return realized profit/loss percentage for ``symbol``."""
        basis = self.closed_basis.get(symbol, 0.0)
        if basis == 0:
            return 0.0
        return self.realized_pnl.get(symbol, 0.0) / basis * 100
