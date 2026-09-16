# AI Safety & LLM Disclosure — FraudShield AI

## Core Principles
1. **Decision Support Only:** Gemini is integrated as an investigation assistant. Gemini NEVER computes the primary fraud risk score and NEVER auto-blocks transactions.
2. **Human Analyst Authority:** The human analyst retains sole decision authority over investigation resolutions (`CONFIRMED_FRAUD`, `FALSE_POSITIVE`).
3. **Backend-Sanitized Evidence Context:** The frontend never communicates with Gemini directly. The FastAPI backend constructs a sanitized evidence context stripping all credentials, passwords, JWT tokens, and unredacted PII.
4. **Prompt Injection Hardening:** The backend service filters injection attempts (e.g. requests for secret keys or internal system instructions).
5. **Clear UI Labeling:** All Copilot outputs are clearly labeled as `AI-generated assistance` with mandatory safety boundary disclaimers.
