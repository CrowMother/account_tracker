import asyncio
import logging
import os
import signal

from client import SchwabClient
from my_secrets import get_secret
from poller import poll_schwab
from tracker import PriceTracker


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_last_week_trades(
    client: SchwabClient, status: str = "FILLED", delta: int = 168
) -> list | None:
    return client.get_account_positions(status, delta)


def main():
    file_path = ".env"
    app_key = get_secret("SCHWAB_APP_KEY", file_path)
    app_secret = get_secret("SCHWAB_APP_SECRET", file_path)
    client = SchwabClient(app_key, app_secret)
    tracker = PriceTracker()

    interval = float(os.getenv("POLL_INTERVAL", 5))
    loop = asyncio.get_event_loop()
    task = loop.create_task(poll_schwab(client, interval, tracker))

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, task.cancel)

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass
    finally:
        logging.info("Polling stopped")


if __name__ == "__main__":
    main()
