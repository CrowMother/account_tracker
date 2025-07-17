import asyncio
import logging

from client import SchwabClient


async def poll_schwab(client: SchwabClient, interval_secs: float = 5) -> None:
    """Continuously poll ``client`` for account positions."""
    while True:
        try:
            client.get_account_positions()
        except Exception as exc:  # pragma: no cover - logging only
            logging.error("Polling error: %s", exc)
        try:
            await asyncio.sleep(interval_secs)
        except asyncio.CancelledError:
            break
