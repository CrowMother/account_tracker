import asyncio
import logging

from client import SchwabClient
from flatten import flatten_dataset
from tracker import PriceTracker
from position_tracker import PositionTracker
from discord_client import send_message
from messaging import format_trade


async def poll_schwab(
    client: SchwabClient,
    interval_secs: float = 5,
    tracker: PriceTracker | None = None,
    position_tracker: PositionTracker | None = None,
    template: str = "Contract {ticker} change {pct_change:.2f}%",
) -> None:
    """Continuously poll ``client`` for account positions.

    Each fetched trade is flattened, fed into ``tracker`` and the percent
    change from the previous price is logged.
    """
    tracker = tracker or PriceTracker()
    position_tracker = position_tracker or PositionTracker()

    while True:
        try:
            data = client.get_account_positions()
            if data:
                trades = flatten_dataset(data)
                for trade in trades:
                    symbol = trade.get("symbol")
                    price = trade.get("price")
                    qty = trade.get("qty")
                    side = trade.get("instruction")
                    if symbol is None or price is None:
                        continue
                    change = tracker.update_and_get_change(
                        symbol, float(price)
                    )
                    if qty is not None and side is not None:
                        try:
                            position_tracker.add_trade(symbol, float(qty), float(price), side)
                        except ValueError as exc:  # pragma: no cover - logging only
                            logging.error("Position tracking error: %s", exc)
                    message = format_trade(
                        template,
                        ticker=symbol,
                        pct_change=change,
                        **trade,
                    )
                    send_message(message)
                    logging.info(
                        "Contract %s change %.2f%%", symbol, change
                    )
        except Exception as exc:  # pragma: no cover - logging only
            logging.error("Polling error: %s", exc)
        try:
            await asyncio.sleep(interval_secs)
        except asyncio.CancelledError:
            break
