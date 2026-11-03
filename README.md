# aegis-ops

**Autonomous Enterprise Governance & Intervention System**
*Track #3: Amazon — Governed AI Agents*

An autonomous procurement & expense claim settlement agent with deterministic pre-tool policy guardrails, human-in-the-loop (HITL) overrides, and a live evaluation dashboard.

---

## 🔒 First-Hour Hackathon Lock-In (Baseline & Target Metrics)

* **Upfront Baseline:** Unpaginated raw LLM agent without deterministic middleware achieves **60% policy compliance** on adversarial/edge-case claims (4 out of 10 unsafe requests slip through via prompt injection or ambiguity).
* **Target Measured Result:** **100% policy enforcement accuracy** across a 20-case evaluation suite (10 compliant, 5 over-budget/restricted items, 5 prompt-injected claims) with **< 15 ms policy interception overhead**.

---

## Repository Architecture

```text
aegis-ops/
├── README.md                  # Shared (Locked in Phase 0)
├── WORKFLOW.md                # Shared Master AI Blueprint (Locked in Phase 0)
├── shared_contract.json       # Shared API Schema (Locked in Phase 0)
├── backend/                   # 🔒 MEMBER A ANTIGRAVITY ONLY (Python + FastAPI)
│   ├── main.py                # FastAPI server & CORS config
│   ├── agent_runner.py        # Multi-step tool-calling agent loop
│   ├── policy_engine.py       # Deterministic pre-execution guardrail interceptor
│   ├── evaluator.py           # 20-case benchmark suite & telemetry calculator
│   └── requirements.txt
└── frontend/                  # 🔒 MEMBER B ANTIGRAVITY ONLY (Vanilla HTML/CSS/JS)
    ├── index.html             # Single-screen 3-pane operator console
    ├── styles.css             # Industrial dark-slate utility styling
    ├── app.js                 # Live polling, trace renderer, & HITL approval actions
    └── mock_fallback.js       # Offline resilience layer if backend disconnects
```

---

## Shared API Contract Summary (`http://localhost:8000`)

* `POST /api/claims/run` — Submit claim for autonomous execution through deterministic guardrails.
* `GET /api/claims/traces` — Retrieve audit trace history with per-step latency and policy verdicts.
* `POST /api/claims/{trace_id}/approve` — Human-In-The-Loop approval or rejection for escalated claims.
* `GET /api/eval/run` — Run 20-case benchmark comparing raw LLM baseline vs. Aegis governed engine.
* `POST /api/simulate/model-outage` — Toggle upstream model outage to verify fail-closed resilience.

---

## Quickstart

### Backend (Member A)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Member B)
```bash
cd frontend
python -m http.server 3000
```
Open `http://localhost:3000` in browser.
