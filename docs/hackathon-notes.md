# Competition & Hackathon Notes — FraudShield AI

## Demo Workflow Steps (End-to-End)
1. **Start Full Stack:** Launch backend (`uvicorn app.main:app`) and frontend (`npm run dev`).
2. **Seed Demo Data:** Run `python scripts/seed_demo.py` to seed default organization, users, and high-risk deterministic transactions.
3. **Login as Analyst:** Login with `analyst@shieldbank.com` / `AnalystPass123!`.
4. **Operations Dashboard:** View live KPIs, Recharts 7-day risk trend area chart, and recent high-risk transactions.
5. **Real-Time Stream:** Run `python scripts/simulate_transactions.py` to stream live synthetic transactions over WebSocket. Watch toast notifications pop up in real time.
6. **Inspect SHAP Factors:** Open a flagged transaction to view exact feature contribution factors (amount deviation, new device, velocity).
7. **Claim Investigation:** Click "Start Investigation", navigate to Investigation workspace tab, and click "Claim Investigation".
8. **Consult Gemini Copilot:** Ask Copilot "Explain top risk factors" or "Summarize evidence" to review AI-assisted evidence summaries.
9. **Record Resolution:** Select "CONFIRMED_FRAUD", enter mandatory resolution notes, and resolve the investigation.
