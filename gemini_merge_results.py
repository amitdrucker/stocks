import os

from google import genai
from google.genai import types

# 1. Setup API Key (Best practice: use environment variable, or paste here for testing)
API_KEY = open('../api_key', 'r').read().strip()
client = genai.Client(
        api_key=API_KEY,
        http_options=types.HttpOptions(api_version="v1beta")  # Force beta version
    )


def merge_gemini_outputs_and_create_table():
    """
    Merge all text files in `gemini_output` into a single prompt, ask Gemini to
    create a simple actions table with columns: symbol, action, reason, and
    save the result to `gemini_output/merged-actions.txt`.
    """
    dir_path = "gemini_output"

    parts = []
    for fname in sorted(os.listdir(dir_path)):
        if not fname.endswith(".txt"):
            continue
        file_path = os.path.join(dir_path, fname)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except Exception as e:
            print(f"Warning: failed to read {file_path}: {e}")
            continue
        if content:
            parts.append(f"--- File: {fname} ---\n{content}")

    if not parts:
        print("No `.txt` files with content found in `gemini_output`.")
        return

    merged_content = "\n\n".join(parts)
    out_path = os.path.join(dir_path, "merged-content.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(merged_content)
    prompt = f"""
You are given multiple Gemini analysis outputs below. Merge them and produce a single simple actions table with columns: symbol, action, reason.
Rules:
- BUY cannot exceed my current cash flow. (after SELLs). if exceeds - use the confidence score of each BUY (10 is highest) and suggest partial buys up to my budget.
- One row per symbol.
- Action should be like: Buy, Fix Stop Loss, Add Stop Loss, Hold, Sell, Reduce, Close - and include quantity and price if applicable.
- Output in a text table format.
- below the output table write: total BUY in $ and total SELL in $

Analyses:
{merged_content}
"""

    try:
        print("Sending merged prompt to Gemini to build actions table...")
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        out_path = os.path.join(dir_path, "merged-actions.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            text = getattr(response, "text", None) or str(response)
            f.write(text)
        print(f"Wrote merged actions to {out_path}")
    except Exception as e:
        print(f"API Error: {e}")