import logging
import time
from datetime import datetime, timezone, timedelta
import requests
import schwabdev


def create_schwab_client(key: str, secret: str):
    """Instantiate and return a Schwabdev client."""
    logging.debug("Initializing Schwabdev client")
    return schwabdev.Client(key, secret)


def get_start_time(delta_hours: int = 1) -> str:
    """Return the UTC ISO timestamp ``delta_hours`` hours ago."""
    start = datetime.now(timezone.utc) - timedelta(hours=delta_hours)
    return start.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def get_end_time() -> str:
    """Return the current time as a UTC ISO timestamp."""
    end = datetime.now(timezone.utc)
    return end.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def retry_request(
    request_func,
    retries: int = 3,
    delay: int = 5,
    backoff: int = 2,
    retry_on=(requests.exceptions.RequestException,),
    raise_on_fail: bool = False,
):
    """Retry a request with exponential backoff."""
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return request_func()
        except retry_on as e:
            last_exc = e
            logging.warning(
                "[Attempt %s] Request failed: %s. Retrying in %ss...",
                attempt,
                e,
                delay,
            )
            time.sleep(delay)
            delay *= backoff
    logging.error("All retry attempts failed.")
    if raise_on_fail and last_exc is not None:
        raise last_exc
    return None


class SchwabClient:
    """Wrapper around schwabdev.Client with retry logic."""

    def __init__(self, key: str, secret: str):
        self.client = create_schwab_client(key, secret)

    def get_account_positions(self, status: str | None = None, hours: int = 168):
        """Return account orders between ``hours`` ago and now."""

        def fetch_orders():
            from_date_str = get_start_time(hours)
            to_date_str = get_end_time()
            return self.client.account_orders_all(
                from_date_str,
                to_date_str,
                None,
                status,
            )

        response = retry_request(fetch_orders, raise_on_fail=True)
        if response is not None and response.status_code == 200:
            return response.json()
        logging.error(
            "Failed to get account positions after retries. Response: %s",
            response,
        )
        return None
