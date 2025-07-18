import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from position_tracker import PositionTracker  # noqa: E402


def test_open_partial_close_and_full_close():
    tracker = PositionTracker()
    tracker.add_trade("AAPL", 10, 100.0, "BUY", "2024-01-19", 170.0)
    tracker.add_trade("AAPL", 10, 105.0, "BUY", "2024-01-19", 170.0)
    tracker.add_trade("AAPL", 15, 110.0, "SELL", "2024-01-19", 170.0)
    assert tracker.get_open_quantity("AAPL", "2024-01-19", 170.0) == 5
    pnl = tracker.calculate_pnl("AAPL", "2024-01-19", 170.0)
    assert round(pnl, 2) == round(125 / 1525 * 100, 2)
    tracker.add_trade("AAPL", 5, 120.0, "SELL", "2024-01-19", 170.0)
    assert tracker.get_open_quantity("AAPL", "2024-01-19", 170.0) == 0
    pnl = tracker.calculate_pnl("AAPL", "2024-01-19", 170.0)
    assert round(pnl, 2) == round(200 / 2050 * 100, 2)
