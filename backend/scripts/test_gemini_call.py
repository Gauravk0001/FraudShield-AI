import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.core.config import settings

api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
print(f"API Key present: {bool(api_key)}, Key prefix: {api_key[:8] if api_key else 'None'}...")

# Test 1: Check google.genai
print("\n--- Test google.genai ---")
try:
    from google import genai
    print("google.genai is imported successfully")
    client = genai.Client(api_key=api_key)
    print("Created genai.Client")
    t0 = time.perf_counter()
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say 'FraudShield Copilot ready' in 5 words."
        )
        print(f"google.genai SUCCESS in {time.perf_counter()-t0:.2f}s: {response.text}")
    except Exception as e:
        print(f"google.genai FAILED in {time.perf_counter()-t0:.2f}s: {type(e).__name__} - {e}")
except ImportError as e:
    print(f"google.genai import failed: {e}")

# Test 2: Check google.generativeai
print("\n--- Test google.generativeai ---")
try:
    import google.generativeai as genai_old
    print("google.generativeai is imported")
    genai_old.configure(api_key=api_key)
    t0 = time.perf_counter()
    try:
        model = genai_old.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Say 'FraudShield Copilot ready' in 5 words.", request_options={"timeout": 5})
        print(f"google.generativeai SUCCESS in {time.perf_counter()-t0:.2f}s: {response.text}")
    except Exception as e:
        print(f"google.generativeai FAILED in {time.perf_counter()-t0:.2f}s: {type(e).__name__} - {e}")
except ImportError as e:
    print(f"google.generativeai import failed: {e}")
