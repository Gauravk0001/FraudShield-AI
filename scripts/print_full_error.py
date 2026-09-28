import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.core.config import settings

api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

from google import genai
client = genai.Client(api_key=api_key)

try:
    res = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents="Say 'FraudShield active' in 3 words."
    )
    print("SUCCESS:", res.text)
except Exception as e:
    print(f"FULL ERROR: {e}")
