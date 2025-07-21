import asyncio
from unittest.mock import Mock

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from poller import poll_schwab  # noqa: E402
from tracker import PriceTracker  # noqa: E402


def test_poll_schwab_calls_client_once(monkeypatch):
    client = Mock()

    async def run_poll():
        monkeypatch.setattr("poller.flatten_dataset", lambda data: [])
        monkeypatch.setattr("poller.send_message", lambda msg: None)
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
            return [
                {
                    "symbol": "AAPL",
                    "price": 100.0,
                    "expiration": "2024-01-19",
                    "strike": 170.0,
                }
            ]

        monkeypatch.setattr("poller.flatten_dataset", fake_flatten)
        sent = []

        monkeypatch.setattr(
            "poller.send_message",
            lambda msg: sent.append(msg),
        )

        task = asyncio.create_task(
            poll_schwab(client, interval_secs=0, tracker=tracker)
        )
        await asyncio.sleep(0.01)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        recorded.append(tracker.last_prices["AAPL"])
        return sent[0]

    message = asyncio.run(run_poll())
    assert recorded == [100.0]
    assert message.startswith("Contract AAPL change")


def test_poll_schwab_custom_template(monkeypatch):
    client = Mock()
    client.get_account_positions.return_value = ["dummy"]

    async def run_poll():
        class DummyTracker:
            def update_and_get_change(self, contract, price):
                return 5.5

        monkeypatch.setattr(
            "poller.flatten_dataset",
            lambda data: [{"symbol": "AAPL", "price": 1.0}],
        )
        sent = []
        monkeypatch.setattr(
            "poller.send_message",
            lambda msg: sent.append(msg),
        )
        task = asyncio.create_task(
            poll_schwab(
                client,
                interval_secs=0,
                tracker=DummyTracker(),
                template="Stock {ticker} {pct_change:.2f}%",
            )
        )
        await asyncio.sleep(0.01)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        return sent[0]

    message = asyncio.run(run_poll())
    assert message == "Stock AAPL 5.50%"


def test_poll_schwab_updates_position_tracker(monkeypatch):
    client = Mock()
    client.get_account_positions.return_value = ["dummy"]

    position = Mock()

    async def run_poll():
        tracker = PriceTracker()

        def fake_flatten(data):
            return [
                {
                    "symbol": "AAPL",
                    "price": 100.0,
                    "qty": 1,
                    "instruction": "BUY",
                    "expiration": "2024-01-19",
                    "strike": 170.0,
                }
            ]

        monkeypatch.setattr("poller.flatten_dataset", fake_flatten)
        monkeypatch.setattr("poller.send_message", lambda msg: None)

        task = asyncio.create_task(
            poll_schwab(
                client,
                interval_secs=0,
                tracker=tracker,
                position_tracker=position,
            )
        )
        await asyncio.sleep(0.01)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(run_poll())
    assert position.add_trade.call_count >= 1
    position.add_trade.assert_any_call(
        "AAPL", 1.0, 100.0, "BUY", "2024-01-19", 170.0
    )


def test_poll_schwab_logs_position_data(monkeypatch, caplog):
    client = Mock()
    client.get_account_positions.return_value = ["dummy"]

    async def run_poll():
        tracker = PriceTracker()

        def fake_flatten(data):
            return [
                {
                    "symbol": "AAPL",
                    "price": 100.0,
                    "qty": 1,
                    "instruction": "BUY",
                    "expiration": "2024-01-19",
                    "strike": 170.0,
                }
            ]

        monkeypatch.setattr("poller.flatten_dataset", fake_flatten)
        monkeypatch.setattr("poller.send_message", lambda msg: None)

        with caplog.at_level("INFO"):
            task = asyncio.create_task(
                poll_schwab(client, interval_secs=0, tracker=tracker)
            )
            await asyncio.sleep(0.01)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    asyncio.run(run_poll())
    assert any("open 1" in record.message for record in caplog.records)


def test_poll_schwab_template_includes_position(monkeypatch):
    client = Mock()
    client.get_account_positions.return_value = ["dummy"]

    async def run_poll():
        tracker = PriceTracker()

        def fake_flatten(data):
            return [
                {
                    "symbol": "AAPL",
                    "price": 100.0,
                    "qty": 1,
                    "instruction": "BUY",
                    "expiration": "2024-01-19",
                    "strike": 170.0,
                }
            ]

        monkeypatch.setattr("poller.flatten_dataset", fake_flatten)
        sent = []
        monkeypatch.setattr(
            "poller.send_message",
            lambda msg: sent.append(msg),
        )

        task = asyncio.create_task(
            poll_schwab(
                client,
                interval_secs=0,
                tracker=tracker,
                template="{open_qty} {pnl:.2f}%",
            )
        )
        await asyncio.sleep(0.01)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        return sent[0]

    message = asyncio.run(run_poll())
    assert message == "1.0 0.00%"


def test_poll_schwab_only_sends_new_trades(monkeypatch):
    """Ensure duplicate trades are not sent multiple times."""
    client = Mock()
    client.get_account_positions.side_effect = [["dummy"], ["dummy"], []]

    async def run_poll():
        tracker = PriceTracker()

        def fake_flatten(data):
            return [
                {
                    "symbol": "AAPL",
                    "price": 100.0,
                    "order_id": 1,
                    "time": "2024-01-01T00:00:00.000Z",
                }
            ]

        monkeypatch.setattr("poller.flatten_dataset", fake_flatten)
        sent = []
        monkeypatch.setattr(
            "poller.send_message",
            lambda msg: sent.append(msg),
        )

        task = asyncio.create_task(
            poll_schwab(client, interval_secs=0, tracker=tracker)
        )
        await asyncio.sleep(0.02)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        return sent

    messages = asyncio.run(run_poll())
    assert len(messages) == 1
