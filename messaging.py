from collections import defaultdict


def format_trade(template: str, **values) -> str:
    """Fill ``template`` with values from ``values``.

    Missing keys are replaced with an empty string rather than raising
    ``KeyError``.
    """
    mapping = defaultdict(str, values)
    return template.format_map(mapping)
