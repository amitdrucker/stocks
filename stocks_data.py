from datetime import datetime

import pandas as pd
import ta
import yfinance as yf


def get_technical_analysis_json(tickers):
    """
    Fetches market data, calculates technical indicators (RSI, MACD, SMA, VRVP),
    and returns a JSON string containing the analysis.

    Args:
        tickers (list): A list of ticker symbols strings, e.g. ["AAPL", "NVDA"]

    Returns:
        str: A JSON formatted string with the results.
    """

    # Helper to fix JSON date serialization issues
    def json_serial(obj):
        if isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    all_results = []
    print(f"Starting analysis for: {tickers}")

    for ticker in tickers:
        try:
            print(f"Processing {ticker}...")

            # 1. FETCH DATA
            # Fetch weekly data for the past 5 years to ensure enough data for calculations
            df = yf.download(ticker, period="5y", interval="1wk", progress=False)

            # Fix for yfinance MultiIndex columns (common in newer versions)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if df.empty:
                print(f"Warning: No data found for {ticker}")
                continue

            # 2. CALCULATE INDICATORS
            # RSI (14 weeks)
            df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

            # SMAs (20, 50, 100, 150 weeks)
            df['SMA_20'] = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
            df['SMA_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
            df['SMA_100'] = ta.trend.SMAIndicator(df['Close'], window=100).sma_indicator()
            df['SMA_150'] = ta.trend.SMAIndicator(df['Close'], window=150).sma_indicator()

            # MACD
            macd = ta.trend.MACD(df['Close'])
            df['MACD'] = macd.macd()
            df['MACD_Signal'] = macd.macd_signal()
            df['MACD_Hist'] = macd.macd_diff()

            # BB
            indicator_bb = ta.volatility.BollingerBands(close=df["Close"], window=20, window_dev=2)
            df['BB_High'] = indicator_bb.bollinger_hband()
            df['BB_Low'] = indicator_bb.bollinger_lband()
            df['BB_Mid'] = indicator_bb.bollinger_mavg()

            # 3. CALCULATE VOLUME PROFILE (VRVP Approx)
            # Use the last 90 weeks for the profile to keep it relevant to current price action
            recent_df = df.tail(90).copy()

            if recent_df.empty:
                continue

            price_bins = 50
            price_min = recent_df['Close'].min()
            price_max = recent_df['Close'].max()
            price_range = price_max - price_min

            if price_range == 0:
                bin_size = 1
            else:
                bin_size = price_range / price_bins

            def get_bin(price):
                # Bin floor logic
                return int((price - price_min) / bin_size) * bin_size + price_min

            recent_df['Price_Bin'] = recent_df['Close'].apply(get_bin)

            # Group by bin and sum volume
            vp_series = recent_df.groupby('Price_Bin')['Volume'].sum()

            # Convert VRVP to list of dicts for JSON
            volume_profile_list = []
            for price_level, volume in vp_series.items():
                volume_profile_list.append({
                    "price_level": round(price_level, 2),
                    "volume": int(volume)
                })

            # 4. STRUCTURE DATA
            # Slice the last 90 candles for the weekly data output
            output_df = df.tail(90).copy()

            # Convert weekly candles dataframe to a dictionary keyed by Date
            candles_dict = {}
            for index, row in output_df.iterrows():
                # Handle potentially missing values (NaN) for JSON compliance
                row_data = row.to_dict()
                cleaned_row = {k: (None if pd.isna(v) else v) for k, v in row_data.items()}

                date_str = index.strftime('%Y-%m-%d')
                candles_dict[date_str] = cleaned_row

            # 5. FINAL OBJECT
            ticker_data = {
                "ticker": ticker,
                "last_updated": datetime.now().isoformat(),
                "weekly_candles": candles_dict,
                "volume_profile": volume_profile_list,
                'rsi': {idx.strftime('%Y-%m-%d'): (None if pd.isna(val) else float(val)) for idx, val in
                        output_df['RSI'].items()},
                "bollinger_bands": {
                    "high": {idx.strftime('%Y-%m-%d'): (None if pd.isna(val) else float(val)) for idx, val in
                             output_df['BB_High'].items()},
                    "mid": {idx.strftime('%Y-%m-%d'): (None if pd.isna(val) else float(val)) for idx, val in
                            output_df['BB_Mid'].items()},
                    "low": {idx.strftime('%Y-%m-%d'): (None if pd.isna(val) else float(val)) for idx, val in
                            output_df['BB_Low'].items()},
                },
                'sma20': {idx.strftime('%Y-%m-%d'): (None if pd.isna(val) else float(val)) for idx, val in
                          output_df['SMA_20'].items()},
                'sma50': {idx.strftime('%Y-%m-%d'): (None if pd.isna(val) else float(val)) for idx, val in
                          output_df['SMA_50'].items()},
                'sma100': {idx.strftime('%Y-%m-%d'): (None if pd.isna(val) else float(val)) for idx, val in
                           output_df['SMA_100'].items()},
                'sma150': {idx.strftime('%Y-%m-%d'): (None if pd.isna(val) else float(val)) for idx, val in
                           output_df['SMA_150'].items()},
                'macd': {idx.strftime('%Y-%m-%d'): (None if pd.isna(val) else float(val)) for idx, val in
                         output_df['MACD'].items()},
                'macd_signal': {idx.strftime('%Y-%m-%d'): (None if pd.isna(val) else float(val)) for idx, val in
                                output_df['MACD_Signal'].items()},
                'macd_hist': {idx.strftime('%Y-%m-%d'): (None if pd.isna(val) else float(val)) for idx, val in
                              output_df['MACD_Hist'].items()}
            }

            all_results.append(ticker_data)

        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
            continue

    return all_results