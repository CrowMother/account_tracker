import logging
from client import SchwabClient
from secrets import get_secret
from flatten import flatten_dataset


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_last_week_trades(client: SchwabClient, status: str = "FILLED", delta: int = 168):
    return client.get_account_positions(status, delta)


def main():
    file_path = ".env"
    app_key = get_secret("SCHWAB_APP_KEY", file_path)
    app_secret = get_secret("SCHWAB_APP_SECRET", file_path)
    client = SchwabClient(app_key, app_secret)

    data = get_last_week_trades(client)
    flattened = flatten_dataset(data)

    if not flattened:
        logging.warning("No flattened data to export.")

    logging.info("Trade data exported to schwab_trades.json")


if __name__ == "__main__":
    main()
