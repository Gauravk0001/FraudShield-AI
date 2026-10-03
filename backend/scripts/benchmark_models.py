import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.core.config import settings

api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

from google import genai
client = genai.Client(api_key=api_key)

candidate_models = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-3-flash-preview",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-2.5-flash-lite"
]

print("=== TESTING CANDIDATE MODELS FOR LATENCY ===")
working_models = []
for m in candidate_models:
    t0 = time.perf_counter()
    try:
        res = client.models.generate_content(
            model=m,
            contents="Say 'FraudShield Copilot operational' in 4 words."
        )
        dt = time.perf_counter() - t0
        text = res.text.strip() if res.text else ""
        print(f"✓ {m}: {dt:.2f}s -> {text}")
        working_models.append((m, dt))
    except Exception as e:
        dt = time.perf_counter() - t0
        print(f"✗ {m}: {dt:.2f}s -> {type(e).__name__}: {str(e)[:80]}")

print("\nWorking models ranked by latency:")
for m, dt in sorted(working_models, key=lambda x: x[1]):
    print(f"  {m}: {dt:.2f}s")
