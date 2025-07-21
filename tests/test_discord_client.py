import os
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from discord_client import send_message  # noqa: E402


@patch('discord_client.requests.post')
def test_send_message_posts(mock_post):
    os.environ['DISCORD_BOT_TOKEN'] = 'abc123'
    os.environ['DISCORD_CHANNEL_ID'] = '42'
    send_message('hi')
    mock_post.assert_called_once_with(
        'https://discord.com/api/v10/channels/42/messages',
        json={'content': 'hi'},
        headers={'Authorization': 'Bot abc123'},
        timeout=10,
    )


@patch('discord_client.requests.post')
def test_send_message_missing_vars(mock_post, caplog, monkeypatch):
    monkeypatch.delenv('DISCORD_BOT_TOKEN', raising=False)
    monkeypatch.delenv('DISCORD_CHANNEL_ID', raising=False)
    with caplog.at_level('ERROR'):
        send_message('hi')
    mock_post.assert_not_called()
    assert 'DISCORD_BOT_TOKEN or DISCORD_CHANNEL_ID not set' in caplog.text
