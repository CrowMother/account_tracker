import asyncio
from unittest.mock import Mock

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from poller import poll_schwab  # noqa: E402
from tracker import PriceTracker  # noqa: E402


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


def test_poll_schwab_tracks_changes(monkeypatch):
    client = Mock()
    client.get_account_positions.return_value = ["dummy"]

    recorded = []

    async def run_poll():
        tracker = PriceTracker()

        def fake_flatten(data):
            return [{"symbol": "AAPL", "price": 100.0}]

        monkeypatch.setattr("poller.flatten_dataset", fake_flatten)

        task = asyncio.create_task(poll_schwab(client, interval_secs=0, tracker=tracker))
        await asyncio.sleep(0.01)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        recorded.append(tracker.last_prices["AAPL"])

    asyncio.run(run_poll())
    assert recorded == [100.0]
