import logging
import os
from dotenv import load_dotenv


def get_secret(key: str, path: str = "./"):
    """Load a single secret from the given dotenv path."""
    try:
        load_dotenv(path)
        value = os.getenv(key)
        if value is None:
            raise Exception("Key not found / is None")
        return value
    except Exception as e:
        logging.error(f"Error getting secret from {path}: {e}")
        return None
