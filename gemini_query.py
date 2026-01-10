import json
import os

from google import genai
from google.genai import types

# 1. Setup API Key (Best practice: use environment variable, or paste here for testing)
API_KEY = open('../api_key', 'r').read().strip()
client = genai.Client(
        api_key=API_KEY,
        http_options=types.HttpOptions(api_version="v1beta")  # Force beta version
    )


def analyze_stock(json_file_path):
    # Use v1beta if the model isn't found on the stable v1 endpoint

    # 2. Load your Stock Data
    try:
        with open(json_file_path, 'r') as f:
            stock_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return

    symbol = stock_data.get('symbol', 'Unknown')

    # 3. Construct the Prompt
    # We embed the instructions and the JSON data into one clear message
    prompt = f"""
    I am a swing trader that does changes on a weekly basis. I check stocks weekly at market close.
    please do technical analysis based on the technical indicators provided in the JSON below following these rules:
    
    
    1. Audit my current position.
    2. Review my Stop Loss (ensure it covers the full position)
    3. Advise on my Free Cash usage (only buy if trend is confirmed)
    4. use min/max in-day prices not close prices for calculations such as stop loss or buy limit price.
    5. for every buy - give score from 1 to 10 about certainty of the buy based on technical analysis (10 being highest confidence)
    6. you can sell partial amount 
    7. avoid over-trading
    8. Provide a neat table of actions.
    
    Stock Data JSON:
    {json.dumps(stock_data, indent=2)}
    """

    # 4. Send to Gemini
    try:
        print(f"Analyzing {symbol}...")
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        # save response to gemini_output\{stock}-advice.txt
        file_path = os.path.join("gemini_output", f"{symbol}-advice.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.text)

    except Exception as e:
        print(f"API Error: {e}")