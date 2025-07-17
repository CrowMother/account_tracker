# Account Tracker

This project retrieves order data from the Schwab Developer API and converts it into a simplified JSON structure. It demonstrates how to authenticate with Schwab, fetch recent trades and flatten them for further analysis.

## Environment Variables

Provide the following variables either in your shell environment or in a `.env` file at the project root:

- `SCHWAB_APP_KEY` – your Schwab API application key
- `SCHWAB_APP_SECRET` – your Schwab API application secret

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

The script requests your recent trades, flattens the nested data and logs a message when processing completes.

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
