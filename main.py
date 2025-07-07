# This is a sample Python script.
import logging
import os
from dotenv import load_dotenv
import schwabdev
from datetime import datetime, timezone, timedelta
import time
import requests
import json
# Press Ctrl+F5 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def create_schwab_client(key, secret):
    logging.debug("Initializing Schwabdev client")
    return schwabdev.Client(key, secret)


def get_end_time(delta=1):
    """
    Returns the current time minus the given delta hours as a string in ISO 8601 format with milliseconds and timezone.

    Args:
        delta: int, optional
            The number of hours to subtract from the current time. Defaults to 1.

    Returns:
        str
            The current time minus delta hours as an ISO 8601 string.
    """

    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(hours=delta)

    # Format dates as ISO 8601 strings with milliseconds and timezone
    return from_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')

def get_start_time(delta=1):
    """
    Returns the current time as a string in ISO 8601 format with milliseconds and timezone,
    adjusted by the given delta hours.

    Args:
        delta: int, optional
            The number of hours to subtract from the current time. Defaults to 1.

    Returns:
        str
            The current time minus delta hours as an ISO 8601 string.
    """
    to_date = datetime.now(timezone.utc)
    # Format dates as ISO 8601 strings with milliseconds and timezone
    return to_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')

def retry_request(request_func, retries=3, delay=5, backoff=2, retry_on=(requests.exceptions.RequestException,), raise_on_fail=False):
    for attempt in range(1, retries + 1):
        try:
            return request_func()
        except retry_on as e:
            logging.warning(f"[Attempt {attempt}] Request failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= backoff

    logging.error("All retry attempts failed.")
    if raise_on_fail:
        raise e  # re-raise the last exception
    return None

class SchwabClient:
    def __init__(self, account, secret):
        self.client = create_schwab_client(app_key, app_secret)

    def get_account_positions(self, status=None, hours=1):
        def fetch_orders():
            to_date_str = get_start_time(hours)
            from_date_str = get_end_time(hours)
            return self.client.account_orders_all(from_date_str, to_date_str, None, status)

        response = retry_request(fetch_orders, raise_on_fail=True)
        if response is not None and response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to get account positions after retries. Response: {response}")
            return None

def get_secret(key, path="./"):
    try:
        load_dotenv(path)
        value = os.getenv(key)
        if value is None:
            #throw error if key not found
            raise Exception ("Key not found / is None")
        return value
    except Exception as e:
        logging.error(f"Error getting secret from {path}: {e}")
        return None

def get_last_week_trades(client, status= "FILLED", delta = 168):
    json_data = client.get_account_positions(status, delta)
    return json_data

def extract_nested_value(obj, path, context=None):
    """
    Safely navigates a nested structure using a list of keys/indexes.
    Supports placeholder substitution like "{leg}".
    """
    context = context or {}
    for key in path:
        # Replace placeholders like "{leg}" using context
        if isinstance(key, str) and key.startswith("{") and key.endswith("}"):
            key = context.get(key.strip("{}"))

        try:
            obj = obj[key]
        except (KeyError, IndexError, TypeError):
            return None
    return obj


def extract_and_append(trade, mapping, leg_index):
    """
    Builds a flat dictionary by extracting values from trade using mapping rules,
    where "{leg}" placeholders are substituted with the given leg index.
    """
    flat = {}
    for key, path in mapping.items():
        flat[key] = extract_nested_value(trade, path, context={"leg": leg_index})
    return flat

def flatten_trade_with_mapping(trade, mapping):
    legs = trade.get("orderLegCollection", [])
    results = []
    for i in range(len(legs)):
        flat = extract_and_append(trade, mapping, i)
        flat["multi_leg"] = len(legs) > 1
        results.append(flat)
    return results

def flatten_data(trade):
    flat_trade = {}

    mapping = {
        "symbol": ["orderLegCollection", "{leg}", "instrument", "symbol"],
        "underlying": ["orderLegCollection", "{leg}", "instrument", "underlyingSymbol"],
        "instruction": ["orderLegCollection", "{leg}", "instruction"],
        "qty": ["orderLegCollection", "{leg}", "quantity"],
        "price": ["orderActivityCollection", 0, "executionLegs", "{leg}", "price"],
        "order_id": ["orderId"],
        "time": ["orderActivityCollection", 0, "executionLegs", "{leg}", "time"],
    }

    flat_trade = flatten_trade_with_mapping(trade, mapping)
    return flat_trade


def flatten_dataset(json_data):
    flat_trades_list = []
    for trade in json_data:
        flat_legs = flatten_data(trade)
        flat_trades_list.extend(flat_legs)  # Use extend, not append
    return flat_trades_list

if __name__ == '__main__':
    file_path = ".env"
    app_key = get_secret("SCHWAB_APP_KEY", file_path)
    app_secret = get_secret("SCHWAB_APP_SECRET", file_path)
    client = SchwabClient(app_key, app_secret)

    data = get_last_week_trades(client)
    flattened = flatten_dataset(data)
    if flattened:
        with open("schwab_trades.json", "w") as f:
            json.dump(flattened, f, indent=2)
        logging.info("Trade data exported to schwab_trades.json")
    else:
        logging.warning("No flattened data to export.")

