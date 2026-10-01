import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.core.config import settings

api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

from google import genai
from google.genai import types

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=4000) # 4 second timeout max
)

for m in ["gemini-3-flash-preview", "gemini-3.1-flash-lite", "gemini-3.7-flash", "gemini-3.8-flash", "gemini-flash-latest"]:
    t0 = time.perf_counter()
    try:
        res = client.models.generate_content(
            model=m,
            contents="Say 'FraudShield ready' in 2 words.",
            config=types.GenerateContentConfig(max_output_tokens=30)
        )
        dt = time.perf_counter() - t0
        print(f"SUCCESS with {m} in {dt:.2f}s: {res.text.strip()}")
        break
    except Exception as e:
        dt = time.perf_counter() - t0
        print(f"FAILED {m} in {dt:.2f}s: {type(e).__name__}: {str(e)[:70]}")
