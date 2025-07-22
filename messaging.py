from collections import defaultdict


DEFAULT_TEMPLATE = (
    "Contract {ticker} change {pct_change:.2f}% {expiration} {strike}"
    " @${price:.2f} {status} {pct_gain:.2f}%"
)


def compose_trade_message(template: str | None = None, **values) -> str:
    """Return a formatted trade message.

    Parameters
    ----------
    template : str | None, optional
        Format string with placeholders. If ``None`` the ``DEFAULT_TEMPLATE``
        is used.
    **values
        Mapping of placeholder values used for formatting.
    """
    template = template or DEFAULT_TEMPLATE
    return format_trade(template, **values)


def format_trade(template: str, **values) -> str:
    """Fill ``template`` with values from ``values``.

    Missing keys are replaced with an empty string rather than raising
    ``KeyError``.
    """
    mapping = defaultdict(str, values)
    return template.format_map(mapping)
