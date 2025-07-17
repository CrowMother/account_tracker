from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from messaging import format_trade  # noqa: E402


def test_format_trade_basic():
    template = 'Stock {ticker} moved {pct_change:.2f}%'
    result = format_trade(template, ticker='AAPL', pct_change=1.23)
    assert result == 'Stock AAPL moved 1.23%'
