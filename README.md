gemini_query.py

This utility reads your `instructions.txt` and every `ticker_*.json` file in `output/`, sends each as a separate request to a configurable Generative/Gemini endpoint, and writes the responses into `gemini_output/`.

Setup

1. Create a Python virtual environment and install dependencies:

   python -m venv .venv; .\.venv\Scripts\Activate; python -m pip install -r requirements.txt

2. Provide credentials in one of two ways:
   - Interactive OAuth: create OAuth client credentials (Desktop app) in Google Cloud Console and download `client_secrets.json`.
   - Existing token: pass `--access-token` with a valid OAuth access token.

Usage

- Using interactive OAuth:

  python gemini_query.py --client-secrets client_secrets.json --model "gemini-3.0-pro"

- Using existing token and custom URL:

  python gemini_query.py --access-token "YOUR_TOKEN" --url "https://generativelanguage.googleapis.com/v1beta2/models/gemini-3.0-pro:generateText"

Notes

- The script sends a simple JSON body with a `prompt` and `metadata`. Adjust `call_endpoint` if your endpoint expects a different payload (e.g., Google GenAI may require a `instances` or `input` field; Vertex AI has different REST endpoints).
- The script will create `gemini_output/` if it doesn't exist and will write one output file per input file.

