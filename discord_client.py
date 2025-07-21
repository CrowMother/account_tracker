import os
import logging
import requests


def send_message(content: str) -> None:
    """Send ``content`` to a Discord channel using a bot token."""
    token = os.getenv("DISCORD_BOT_TOKEN")
    channel_id = os.getenv("DISCORD_CHANNEL_ID")

    if not token or not channel_id:
        logging.error("DISCORD_BOT_TOKEN or DISCORD_CHANNEL_ID not set")
        return

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {token}"}

    try:
        requests.post(
            url, json={"content": content}, headers=headers, timeout=10
        )
    except requests.RequestException as exc:  # pragma: no cover - logging only
        logging.error("Failed to send Discord message: %s", exc)
