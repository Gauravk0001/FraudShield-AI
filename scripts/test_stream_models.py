import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.core.config import settings

api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)

candidate_models = [
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-3-flash-preview",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
]

print("=== TESTING FAST MODELS (1 ATTEMPT, NO RETRIES) ===")
for m in candidate_models:
    t0 = time.perf_counter()
    try:
        # Test generate_content_stream
        stream = client.models.generate_content_stream(
            model=m,
            contents="Say 'FraudShield active' in 3 words.",
            config=types.GenerateContentConfig(
                max_output_tokens=150,
                temperature=0.2,
            )
        )
        first_chunk_time = None
        full_text = []
        for chunk in stream:
            if first_chunk_time is None:
                first_chunk_time = time.perf_counter() - t0
            if chunk.text:
                full_text.append(chunk.text)
        total_time = time.perf_counter() - t0
        print(f"[SUCCESS] {m}: First chunk in {first_chunk_time:.2f}s, Total {total_time:.2f}s -> {''.join(full_text).strip()}")
    except Exception as e:
        dt = time.perf_counter() - t0
        print(f"[FAILED]  {m}: {dt:.2f}s -> {type(e).__name__}: {str(e)[:100]}")
