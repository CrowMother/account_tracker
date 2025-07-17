import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tracker import PriceTracker  # noqa: E402


def test_update_and_get_change():
    tracker = PriceTracker()
    first = tracker.update_and_get_change("AAPL", 100.0)
    second = tracker.update_and_get_change("AAPL", 110.0)
    assert first == 0.0
    assert round(second, 2) == 10.0
