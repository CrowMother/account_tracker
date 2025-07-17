import os
import logging
import requests


def send_message(content: str) -> None:
    """Send ``content`` to a Discord channel via webhook."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        logging.error("DISCORD_WEBHOOK_URL not set")
        return
    try:
        requests.post(webhook_url, json={"content": content}, timeout=10)
    except requests.RequestException as exc:  # pragma: no cover - logging only
        logging.error("Failed to send Discord message: %s", exc)
