class PositionTracker:
    """Track open positions and realized PnL using FIFO cost basis.

    Positions are keyed by ``symbol``, ``expiration`` and ``strike`` so that
    multiple option contracts for the same underlying can be tracked
    independently.
    """

    def __init__(self):
        # queue of lots per (symbol, expiration, strike)
        self.positions: dict[
            tuple[str, str, float], list[dict[str, float]]
        ] = {}
        # realized profit in dollars per key
        self.realized_pnl: dict[tuple[str, str, float], float] = {}
        # total cost basis for closed lots per key
        self.closed_basis: dict[tuple[str, str, float], float] = {}

    @staticmethod
    def _build_key(
        symbol: str, expiration: str | None, strike: float | None
    ) -> tuple[str, str, float]:
        """Return a normalized composite key for internal dictionaries."""
        return (symbol, expiration or "", float(strike or 0.0))

    def add_trade(
        self,
        symbol: str,
        qty: float,
        price: float,
        side: str,
        expiration: str | None = None,
        strike: float | None = None,
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
        expiration: str | None, optional
            Option expiration date.
        strike: float | None, optional
            Option strike price.
        """
        side = side.upper()
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")

        key = self._build_key(symbol, expiration, strike)
        queue = self.positions.setdefault(key, [])
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
            self.realized_pnl[key] = self.realized_pnl.get(key, 0.0) + pnl
            self.closed_basis[key] = (
                self.closed_basis.get(key, 0.0) + lot["price"] * close_qty
            )
            qty_remaining -= close_qty

    def get_open_quantity(
        self,
        symbol: str,
        expiration: str | None = None,
        strike: float | None = None,
    ) -> float:
        """Return the remaining open quantity for the given contract."""
        key = self._build_key(symbol, expiration, strike)
        queue = self.positions.get(key, [])
        return sum(lot["qty"] for lot in queue)

    def calculate_pnl(
        self,
        symbol: str,
        expiration: str | None = None,
        strike: float | None = None,
    ) -> float:
        """Return realized profit/loss percentage for the given contract."""
        key = self._build_key(symbol, expiration, strike)
        basis = self.closed_basis.get(key, 0.0)
        if basis == 0:
            return 0.0
        return self.realized_pnl.get(key, 0.0) / basis * 100
