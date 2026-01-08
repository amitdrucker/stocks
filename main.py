import os
from collections import defaultdict

import my_portfolio
from gemini_merge_results import merge_gemini_outputs_and_create_table
from gemini_query import analyze_stock
from result_splitter import split_portfolio_data

def sendToGemini():
    output_dir = 'output'
    for fn in os.listdir(output_dir):
        file_path = os.path.join(output_dir, fn)
        if os.path.isfile(file_path):
            analyze_stock(file_path)

def empty_folders():
    output_dir = 'output'
    gemini_dir = 'gemini_output'

    # empty `gemini_output` folder first
    if os.path.isdir(gemini_dir):
        for root, dirs, files in os.walk(gemini_dir, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except OSError:
                    pass
    # empty `output` folder first
    if os.path.isdir(output_dir):
        for root, dirs, files in os.walk(output_dir, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except OSError:
                    pass

def enrich_portfolio(data):
    candidates = ["AMD",
                  "TSM",
                  "INTC",
                  "PLTR",
                  "AAPL",
                  "SANM",
                  "AVGO",
                  "HOOD",
                  "OKLO",
                  "ESTC",
                  "VRT",
                  "MSFT",
                  "SANM",
                  "ORCL",
                  "TSLA",
                  "AMZN",
                  "SEDG",
                  "COHU",
                  "COMP",
                  "META",
                  "SEDG",
                  "NNE",
                  "MP",
                  "XOM",
                  "SOFI"]

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

    split_portfolio_data(data)

    del data["open_orders"]
    del data["account"]
    return data


empty_folders()
input_json = my_portfolio.get_portfolio_json()
enriched_data = enrich_portfolio(input_json)
sendToGemini()
merge_gemini_outputs_and_create_table()