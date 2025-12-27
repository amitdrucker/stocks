import json
from collections import defaultdict

import my_portfolio


def enrich_portfolio(data):
    candidates = ["AMD",
                  "AVGO",
                  "MSFT",
                  "SANM",
                  "ORCL",
                  "TSLA",
                  "AMZN",
                  "INTL",
                  "META"]

    # 1. Group open orders by symbol
    orders_map = defaultdict(list)
    for order in data.get("open_orders", []):
        orders_map[order["symbol"]].append(order)

    # Track all symbols currently in the portfolio
    portfolio_symbols = set()

    # 2. Merge orders into positions
    for position in data.get("positions", []):
        symbol = position["symbol"]
        portfolio_symbols.add(symbol)

        # Add matching orders to the position
        position["active_orders"] = orders_map.get(symbol, [])

    # Filter: Only keep candidates that are NOT in the current portfolio
    data["interesting_symbols"] = [
        sym for sym in candidates
        if sym not in portfolio_symbols
    ]

    del data["open_orders"]
    del data["account"]
    return data


input_json = my_portfolio.get_portfolio_json()
enriched_data = enrich_portfolio(input_json)
open('output/output.json', 'w').write(json.dumps(enriched_data, indent=4))
