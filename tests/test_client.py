from unittest.mock import Mock, patch
import sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("schwabdev", Mock())

from client import SchwabClient


@patch('client.create_schwab_client')
@patch('client.time.sleep', return_value=None)
def test_get_account_positions_retries(mock_sleep, mock_create):
    mock_api = Mock()
    mock_create.return_value = mock_api

    success_response = Mock()
    success_response.status_code = 200
    success_response.json.return_value = {'ok': True}

    def side_effect(*args, **kwargs):
        if side_effect.calls < 2:
            side_effect.calls += 1
            raise requests.exceptions.RequestException('fail')
        return success_response
    side_effect.calls = 0

    mock_api.account_orders_all.side_effect = side_effect

    client = SchwabClient('key', 'secret')
    result = client.get_account_positions()

    assert result == {'ok': True}
    assert mock_api.account_orders_all.call_count == 3
    assert mock_sleep.call_count == 2
