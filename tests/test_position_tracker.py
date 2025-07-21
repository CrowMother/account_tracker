import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from position_tracker import PositionTracker  # noqa: E402


def test_open_partial_close_and_full_close():
    tracker = PositionTracker()
    tracker.add_trade("AAPL", 10, 100.0, "BUY", "2024-01-19", 170.0)
    tracker.add_trade("AAPL", 10, 105.0, "BUY", "2024-01-19", 170.0)
    pnl_trade = tracker.add_trade(
        "AAPL", 15, 110.0, "SELL", "2024-01-19", 170.0
    )
    assert pnl_trade == 125.0
    assert tracker.get_open_quantity("AAPL", "2024-01-19", 170.0) == 5
    pnl = tracker.calculate_pnl("AAPL", "2024-01-19", 170.0)
    assert round(pnl, 2) == round(125 / 1525 * 100, 2)
    pnl_trade = tracker.add_trade(
        "AAPL", 5, 120.0, "SELL", "2024-01-19", 170.0
    )
    assert pnl_trade == 75.0
    assert tracker.get_open_quantity("AAPL", "2024-01-19", 170.0) == 0
    pnl = tracker.calculate_pnl("AAPL", "2024-01-19", 170.0)
    assert round(pnl, 2) == round(200 / 2050 * 100, 2)


def test_fifo_by_contract():
    """Lots with different expiration/strike should be tracked separately."""
    tracker = PositionTracker()

    # Open two contracts for the same symbol but different option details
    tracker.add_trade("AAPL", 10, 100.0, "BUY", "2024-01-19", 170.0)
    tracker.add_trade("AAPL", 5, 50.0, "BUY", "2024-02-16", 175.0)

    # Close only the first contract
    pnl_trade = tracker.add_trade(
        "AAPL", 10, 120.0, "SELL", "2024-01-19", 170.0
    )
    assert pnl_trade == 200.0

    assert tracker.get_open_quantity("AAPL", "2024-01-19", 170.0) == 0
    assert tracker.get_open_quantity("AAPL", "2024-02-16", 175.0) == 5
    pnl_first = tracker.calculate_pnl("AAPL", "2024-01-19", 170.0)
    pnl_second = tracker.calculate_pnl("AAPL", "2024-02-16", 175.0)
    assert round(pnl_first, 2) == round(200 / 1000 * 100, 2)
    assert pnl_second == 0.0
