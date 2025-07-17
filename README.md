# Account Tracker

This project retrieves order data from the Schwab Developer API and converts it into a simplified JSON structure. It demonstrates how to authenticate with Schwab, fetch recent trades and flatten them for further analysis.

## Environment Variables

Provide the following variables either in your shell environment or in a `.env` file at the project root:

- `SCHWAB_APP_KEY` – your Schwab API application key
- `SCHWAB_APP_SECRET` – your Schwab API application secret
- `POLL_INTERVAL` – (optional) seconds between API polls, default `5`
- `DISCORD_WEBHOOK_URL` – (optional) Discord webhook URL to send trade updates

## Installation

1. Ensure Python 3.12 or newer is available.
2. (Optional) Create and activate a virtual environment.
3. Install the dependencies defined in `pyproject.toml`:
   ```bash
   pip install -e .
   ```

## Running

With the environment variables configured, execute:

```bash
python main.py
```

The script continuously polls Schwab for account positions using the interval set in `POLL_INTERVAL` (default `5` seconds) and logs results until stopped with `Ctrl+C`.

### Output Format

The flattened data is a list of JSON objects. Each object contains keys similar to the example below:

```json
{
  "symbol": "AAPL",
  "underlying": "AAPL",
  "instruction": "BUY",
  "qty": 10,
  "price": 123.45,
  "order_id": 123456789,
  "time": "2024-01-01T12:34:56.000Z",
  "multi_leg": false
}
```

These objects can be written to a file or further processed as needed.

### Trade Messages

Each flattened trade is formatted into a short string before being sent to
Discord (if `DISCORD_WEBHOOK_URL` is configured). The default template is:

```
Contract {ticker} change {pct_change:.2f}%
```

The template accepts any keys from the flattened trade dictionary, plus the
calculated `pct_change` from the `PriceTracker`. For instance, a more detailed
template could look like:

```
{ticker} {price} {strike} {open_close} {pct_change}
```

Which might produce an output similar to:

```
AAPL 175.00 170C OPEN 0.50%
```

To use a custom template, pass it to `poll_schwab()` or modify the call in
`main.py`.
