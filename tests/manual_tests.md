# Manual Test Scenarios

## main.py

1. **Missing Environment Variables**
   - Unset `SCHWAB_APP_KEY` or `SCHWAB_APP_SECRET` and run `python main.py`.
   - Verify that an error is logged about missing secrets.

2. **Missing tokens.json**
   - Rename `tokens.json` and execute `python main.py`.
   - Confirm the application warns about authentication failure.

3. **API Rate Limiting**
   - Simulate repeated polling causing rate limit errors.
   - Ensure the poller logs retry attempts and continues running.
