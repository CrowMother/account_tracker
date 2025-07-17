from __future__ import annotations


def extract_nested_value(obj, path, context: dict | None = None):
    """Safely navigate a nested structure using a list of keys/indexes."""
    context = context or {}
    for key in path:
        if isinstance(key, str) and key.startswith("{") and key.endswith("}"):
            key = context.get(key.strip("{}"))
        try:
            obj = obj[key]
        except (KeyError, IndexError, TypeError):
            return None
    return obj


def extract_and_append(trade, mapping, leg_index):
    """Build a flat dictionary using mapping rules and leg index."""
    flat = {}
    for key, path in mapping.items():
        flat[key] = extract_nested_value(trade, path, context={"leg": leg_index})
    return flat


def flatten_trade_with_mapping(trade, mapping):
    legs = trade.get("orderLegCollection", [])
    results = []
    for i in range(len(legs)):
        flat = extract_and_append(trade, mapping, i)
        flat["multi_leg"] = len(legs) > 1
        results.append(flat)
    return results


def flatten_data(trade):
    mapping = {
        "symbol": ["orderLegCollection", "{leg}", "instrument", "symbol"],
        "underlying": ["orderLegCollection", "{leg}", "instrument", "underlyingSymbol"],
        "instruction": ["orderLegCollection", "{leg}", "instruction"],
        "qty": ["orderLegCollection", "{leg}", "quantity"],
        "price": ["orderActivityCollection", 0, "executionLegs", "{leg}", "price"],
        "order_id": ["orderId"],
        "time": ["orderActivityCollection", 0, "executionLegs", "{leg}", "time"],
    }
    return flatten_trade_with_mapping(trade, mapping)


def flatten_dataset(json_data):
    flat_trades_list = []
    for trade in json_data:
        flat_legs = flatten_data(trade)
        flat_trades_list.extend(flat_legs)
    return flat_trades_list
