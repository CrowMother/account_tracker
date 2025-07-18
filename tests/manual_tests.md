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
6. **Position Tracking**
   - Execute a sequence of buy and sell trades.
   - Verify that open quantities and realized PnL are updated according to FIFO logic.

## Docker Usage

1. **Build the Docker image**
   - Run `docker build -t account-tracker .` from the project root.
   - Ensure the build completes without errors.

2. **Run container with minimal variables**
   - Execute `docker run -e SCHWAB_APP_KEY=your_key -e SCHWAB_APP_SECRET=your_secret account-tracker`.
   - The container should start and begin polling.

3. **Validate startup logs**
   - Check `docker logs` for lines starting with `Contract` which indicate polling has begun.
