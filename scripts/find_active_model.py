import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.core.config import settings

api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

from google import genai
client = genai.Client(api_key=api_key)

print("Listing models...")
try:
    for m in client.models.list():
        if "generateContent" in (getattr(m, "supported_generation_methods", []) or getattr(m, "supported_actions", [])) or "gemini" in m.name.lower():
            print(f"Model: {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

test_models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-3.8-flash", "gemini-2.0-flash-exp"]
for tm in test_models:
    try:
        res = client.models.generate_content(
            model=tm,
            contents="Say 'FraudShield active' in 3 words."
        )
        print(f"SUCCESS with {tm}: {res.text.strip()}")
        break
    except Exception as e:
        print(f"Failed {tm}: {e}")
