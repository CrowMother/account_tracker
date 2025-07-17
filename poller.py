import asyncio
import logging

from client import SchwabClient
from flatten import flatten_dataset
from tracker import PriceTracker


async def poll_schwab(
    client: SchwabClient,
    interval_secs: float = 5,
    tracker: PriceTracker | None = None,
) -> None:
    """Continuously poll ``client`` for account positions.

    Each fetched trade is flattened, fed into ``tracker`` and the percent
    change from the previous price is logged.
    """
    tracker = tracker or PriceTracker()

    while True:
        try:
            data = client.get_account_positions()
            if data:
                trades = flatten_dataset(data)
                for trade in trades:
                    symbol = trade.get("symbol")
                    price = trade.get("price")
                    if symbol is None or price is None:
                        continue
                    change = tracker.update_and_get_change(symbol, float(price))
                    logging.info(
                        "Contract %s change %.2f%%", symbol, change
                    )
        except Exception as exc:  # pragma: no cover - logging only
            logging.error("Polling error: %s", exc)
        try:
            await asyncio.sleep(interval_secs)
        except asyncio.CancelledError:
            break

