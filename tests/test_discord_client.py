import os
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from discord_client import send_message  # noqa: E402


@patch('discord_client.requests.post')
def test_send_message_posts(mock_post):
    os.environ['DISCORD_WEBHOOK_URL'] = 'http://localhost/webhook'
    send_message('hi')
    mock_post.assert_called_once_with(
        'http://localhost/webhook', json={'content': 'hi'}, timeout=10
    )


@patch('discord_client.requests.post')
def test_send_message_no_url(mock_post, caplog, monkeypatch):
    monkeypatch.delenv('DISCORD_WEBHOOK_URL', raising=False)
    with caplog.at_level('ERROR'):
        send_message('hi')
    mock_post.assert_not_called()
    assert 'DISCORD_WEBHOOK_URL not set' in caplog.text
