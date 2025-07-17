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

4. **Price Tracking**
   - Run the poller with sample trades and verify that price changes are logged
     correctly for each contract.
5. **Discord Notifications**
   - Set `DISCORD_WEBHOOK_URL` to a test webhook and run the poller.
   - Confirm messages are sent with the configured template.
