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
   - Set `DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_ID` in your environment.
   - Run the poller and confirm messages appear in the channel.
6. **Position Tracking**
   - Execute a sequence of buy and sell trades.
   - Verify that open quantities and realized PnL are updated according to FIFO logic.
   - Observe the log output for open contract count and win/loss percentage after each trade.
7. **Partial Close Handling**
   - Buy 10 contracts of a symbol and then buy another 10 at a different price.
   - Sell 15 contracts and confirm the open quantity is reduced to 5.
   - Check that the first lot is closed entirely and that PnL is calculated using its purchase price plus part of the second lot.
8. **FIFO P/L Calculation**
   - Sell the remaining 5 contracts at a third price.
   - The open quantity should return to zero.
   - Verify the win/loss percentage equals total realized profit divided by the cost basis of the closed lots.

9. **Trade Lifecycle with Discord Confirmation**
   - Set `SCHWAB_APP_KEY`, `SCHWAB_APP_SECRET`, `DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_ID` in your environment.
   - Run `python main.py` so trades are processed and messages are sent.
   - Execute a series of buys and sells that first partially close and then fully close a position.
   - Observe the log output for open quantity and PnL after each trade.
   - Check the Discord channel for messages showing `Opening`, `Partially Closed` and `Fully Closed` statuses along with the correct gain percentages.
   - Ensure each message displays the gain formatted as a percentage next to the status.

## Docker Usage

1. **Build the Docker image**
   - Run `docker build -t account-tracker .` from the project root.
   - Ensure the build completes without errors.

2. **Run container with minimal variables**
   - Execute `docker run -e SCHWAB_APP_KEY=your_key -e SCHWAB_APP_SECRET=your_secret account-tracker`.
   - The container should start and begin polling.

3. **Validate startup logs**
   - Check `docker logs` for lines starting with `Contract` which indicate polling has begun.
