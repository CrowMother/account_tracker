import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flatten import flatten_data, flatten_dataset

FIXTURE = Path(__file__).parent / "fixtures" / "sample_orders.json"

with open(FIXTURE) as f:
    SAMPLE_ORDERS = json.load(f)


def test_flatten_data_single():
    result = flatten_data(SAMPLE_ORDERS[0])
    expected = [{
        "symbol": "AAPL",
        "underlying": "AAPL",
        "instruction": "BUY",
        "qty": 10,
        "price": 100.0,
        "order_id": 1,
        "time": "2024-01-01T00:00:00.000Z",
        "multi_leg": False
    }]
    assert result == expected


def test_flatten_dataset_full():
    result = flatten_dataset(SAMPLE_ORDERS)
    expected = [
        {
            "symbol": "AAPL",
            "underlying": "AAPL",
            "instruction": "BUY",
            "qty": 10,
            "price": 100.0,
            "order_id": 1,
            "time": "2024-01-01T00:00:00.000Z",
            "multi_leg": False
        },
        {
            "symbol": "MSFT",
            "underlying": "MSFT",
            "instruction": "SELL",
            "qty": 5,
            "price": 200.0,
            "order_id": 2,
            "time": "2024-01-02T00:00:00.000Z",
            "multi_leg": True
        },
        {
            "symbol": "MSFT",
            "underlying": "MSFT",
            "instruction": "BUY",
            "qty": 5,
            "price": 201.0,
            "order_id": 2,
            "time": "2024-01-02T00:00:00.000Z",
            "multi_leg": True
        }
    ]
    assert result == expected
