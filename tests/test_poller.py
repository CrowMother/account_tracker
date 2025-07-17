import asyncio
from unittest.mock import Mock

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from poller import poll_schwab  # noqa: E402


def test_poll_schwab_calls_client_once():
    client = Mock()

    async def run_poll():
        task = asyncio.create_task(poll_schwab(client, interval_secs=0))
        await asyncio.sleep(0.01)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(run_poll())
    assert client.get_account_positions.called
