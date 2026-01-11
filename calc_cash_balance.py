import json
import yfinance as yf


def calculate_projected_cash(json_file_path):
    # 1. Load the portfolio data
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
        return

    current_cash = data.get('cash_usd', 0.0)
    open_orders = data.get('open_orders', [])

    print(f"Starting Cash Balance: ${current_cash:,.2f}")
    print("-" * 50)

    # 2. Filter orders (Ignore STP) and collect symbols
    valid_orders = [o for o in open_orders if o['type'] != 'STP']
    unique_symbols = list(set(o['symbol'] for o in valid_orders))

    if not unique_symbols:
        print("No active Market or Limit orders found to process.")
        return

    # 3. Fetch current market prices for valid orders
    print(f"Fetching current prices for: {', '.join(unique_symbols)}...")
    tickers = yf.Tickers(' '.join(unique_symbols))

    # projected cash accumulator
    projected_cash = current_cash

    print("\nProcessing Orders:")
    print(f"{'ACTION':<6} {'QTY':<5} {'SYMBOL':<6} {'TYPE':<4} {'EST. PRICE':<12} {'IMPACT':<12}")

    for order in valid_orders:
        symbol = order['symbol']
        action = order['action']
        qty = order['qty']
        order_type = order['type']

        # Get current price
        # Note: 'regularMarketPrice' is standard, but we use a fallback to 'previousClose' if market is closed/data missing
        try:
            ticker_info = tickers.tickers[symbol].info
            # Prioritize current price, fallback to previous close
            price = ticker_info.get('currentPrice') or ticker_info.get('regularMarketPrice') or ticker_info.get(
                'previousClose', 0.0)
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            price = 0.0

        if price == 0.0:
            print(f"Skipping {symbol} (Price not found)")
            continue

        # Calculate trade value
        trade_value = qty * price

        # 4. Update Cash Balance
        if action == 'BUY':
            projected_cash -= trade_value
            impact_str = f"-${trade_value:,.2f}"
        elif action == 'SELL':
            projected_cash += trade_value
            impact_str = f"+${trade_value:,.2f}"

        print(f"{action:<6} {qty:<5} {symbol:<6} {order_type:<4} ${price:<11,.2f} {impact_str:<12}")

    print("-" * 50)
    print(f"Projected Cash Balance: ${projected_cash:,.2f}")


if __name__ == "__main__":
    # Ensure your file is named 'portfolio.json' and is in the same folder
    calculate_projected_cash('output/portfolio.json')