# This is a sample Python script.
import logging
import os
from dotenv import load_dotenv
import schwabdev
# Press Ctrl+F5 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def create_schwab_client(key, secret):
    logging.debug("Initializing Schwabdev client")
    return schwabdev.Client(key, secret)

class SchwabClient:
    def __init__(self, account, secret):
        self.client = create_schwab_client(app_key, app_secret)


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

if __name__ == '__main__':
    file_path = ""
    app_key = get_secret("SCHWAB_APP_KEY", file_path)
    app_secret = get_secret("SCHWAB_APP_SECRET", file_path)
    client = SchwabClient(app_key, app_secret)