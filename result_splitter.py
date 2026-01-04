import json

from stocks_data import get_technical_analysis_json


def split_portfolio_data(data):

    # ---------------------------------------------------------
    # PART 2: SAVE PER-TICKER JSONs
    # ---------------------------------------------------------
    # We need to collect every symbol found in Positions, Orders, OR Technical Data
    all_symbols = set()

    # Create lookup maps for faster access
    positions_map = {p['symbol']: p for p in data.get('positions', [])}
    technical_map = {t['ticker']: t for t in data.get('technical_data', [])}

    # Group orders by symbol
    orders_map = {}
    for order in data.get('open_orders', []):
        sym = order.get('symbol')
        if sym:
            if sym not in orders_map:
                orders_map[sym] = []
            orders_map[sym].append(order)

    # Gather all unique symbols from all sources
    all_symbols.update(positions_map.keys())
    all_symbols.update(technical_map.keys())
    all_symbols.update(orders_map.keys())
    all_symbols.update(data.get('interesting_symbols'))

    print(f"Found {len(all_symbols)} unique symbols. Splitting files...")

    for sym in sorted(all_symbols):
        # 1. Get Position Data (default to 0 if not held)
        pos = positions_map.get(sym, {})
        shares = pos.get('shares', 0.0)
        avg_cost = pos.get('avg_cost', 0.0)

        # 2. Get Open Orders (default to empty list)
        sym_orders = orders_map.get(sym, [])

        # 3. Get Technical Data (default to None/Empty)
        tech_data = technical_map.get(sym, {})

        # 4. Construct the per-ticker object
        ticker_obj = {
            "free_cash": data.get("cash_usd", 0.0),
            "symbol": sym,
            "shares": shares,
            "avg_cost": avg_cost,
            "open_orders": sym_orders,
            "technical_data": get_technical_analysis_json([sym])[0]
        }

        # 5. Save to file
        filename = f"ticker_{sym}.json"
        with open('output/'+filename, 'w') as f:
            json.dump(ticker_obj, f, indent=4)

        print(f" -> Created {filename}")