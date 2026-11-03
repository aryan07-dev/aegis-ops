# MASTER AI SYSTEM PROMPT & WORKFLOW BLUEPRINT (ANTIGRAVITY EDITION)

## 1. Project Identity & Anti-"AI Slop" Manifesto

* **Project Name:** `aegis-ops` (Autonomous Enterprise Governance & Intervention System)
* **Track:** #3 Amazon — Governed AI Agents
* **Environment:** Antigravity IDE / Terminal Agent running directly inside the active GitHub repository root.
* **Use Case:** An autonomous procurement & expense claim settlement agent that parses multi-step employee reimbursement requests, cross-checks vendor registries, executes payouts, enforces deterministic policy rules, logs telemetry to an evaluation dashboard, and halts for human-in-the-loop (HITL) approval on risky actions.

### STRICT ANTI-AI SLOP RULES (MANDATORY FOR ALL GENERATED CODE)

1. **NO Generic AI Aesthetics:** Ban all purple/indigo gradients, neon glowing borders, glassmorphism, floating sparkle icons (`✨`, `🤖`), and marketing landing pages. The app must open directly into a dense, functional, industrial utility workspace (inspired by Linear, Stripe Dashboard, or AWS Console).
2. **Color & Typography:** Use a high-contrast slate/zinc palette (`#09090B` background, `#18181B` panels, `#27272A` 1px solid borders, `#FAFAFA` primary text, `#A1A1AA` muted text). Use semantic status badges only: Emerald (`#10B981`) for `ALLOWED`, Amber (`#F59E0B`) for `PENDING_HUMAN_APPROVAL`, and Crimson (`#EF4444`) for `POLICY_VIOLATION`. Use `Inter` or `system-ui` for labels and `JetBrains Mono` for all IDs, dollar amounts, timestamps, latency metrics, and JSON payloads.
3. **NO Chatbots:** Do not build a conversational chat bubble UI. Build a **Transaction & Execution Console** where inputs are structured claim forms/JSON payloads and outputs are step-by-step deterministic execution traces.
4. **NO Hallucinated Placeholders:** Never use `// TODO`, `Lorem ipsum`, or fake `setTimeout` delays pretending to be AI. Every button must trigger a real state transition or API call.

---

## 2. MANDATORY ANTIGRAVITY TERMINAL & GIT EXECUTION DIRECTIVES

**CRITICAL DIRECTIVE FOR ANTIGRAVITY AGENT:**
You are already operating inside the local GitHub repository terminal. You must use your native file-creation tools and terminal execution tool to build, verify, stage, commit, and push code autonomously.

1. **Context Awareness (Already in Repo):** Do **NOT** run `git init` or `git clone` if `.git` already exists in the current working directory. First run `git status` and `git branch` in the terminal to inspect the repository state.
2. **Non-Interactive Terminal Commands:** Always run terminal commands non-interactively (no pagers, no interactive prompts). Chain git operations cleanly (e.g., `git add <files> && git commit -m "<msg>" && git push origin <branch>`).
3. **Autonomous Terminal Commits:** After completing each task module, immediately execute the corresponding `git add`, `git commit`, and `git push` commands in the Antigravity terminal without waiting for manual user intervention.
4. **Directory Isolation Guardrail:**
   * If you are **Member A's Antigravity Agent**, NEVER run `git add .` or `git add -A` after Phase 0. Always run `git add backend/` to ensure you never stage or overwrite frontend files.
   * If you are **Member B's Antigravity Agent**, NEVER run `git add .` or `git add -A`. Always run `git add frontend/` to ensure you never stage or overwrite backend files.
5. **Pre-Commit Verification:** Before executing any `git commit`, run a quick syntax/compile check in the terminal (e.g., `python3 -m py_compile backend/*.py` for Member A, or `node --check frontend/app.js` for Member B) so broken states are never pushed.

---

## 3. First-Hour Hackathon Lock-In (Rubric Requirement)

*Must be committed to `README.md` in the first hour and never changed:*

* **Upfront Baseline:** Unpaginated raw LLM agent without deterministic middleware achieves **60% policy compliance** on adversarial/edge-case claims (4 out of 10 unsafe requests slip through via prompt injection or ambiguity).
* **Target Measured Result:** **100% policy enforcement accuracy** across a 20-case evaluation suite (10 compliant, 5 over-budget/restricted items, 5 prompt-injected claims) with $< 15\text{ ms}$ **policy interception overhead**.

---

## 4. Repository Architecture & Strict File Ownership

To allow **Member A** and **Member B** to run Antigravity simultaneously on two laptops without merge conflicts, neither agent may edit files outside their assigned directory after Phase 0 setup.

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

## 5. Shared API Contract (`shared_contract.json`)

Both Antigravity agents must build strictly against these endpoints (`http://localhost:8000`):

* `POST /api/claims/run`
  * **Payload:** `{ "employee_id": "EMP-402", "vendor": "AWS Cloud", "category": "Infrastructure", "amount": 420.00, "notes": "Q3 Server Cluster" }`
  * **Response:** Returns execution trace and policy verdict (`PASSED`, `PAUSED_HITL`, `BLOCKED`).
* `GET /api/claims/traces`
  * **Response:** Returns array of all executed claims, step-by-step tool calls, policy check statuses, and latency in $\text{ms}$.
* `POST /api/claims/{trace_id}/approve`
  * **Payload:** `{ "decision": "APPROVE" | "REJECT", "reviewer_note": "Verified with VP" }`
  * **Response:** Resumes or terminates a paused agent run.
* `GET /api/eval/run`
  * **Response:** Runs the 20-test dataset against the baseline vs. governed agent and returns live accuracy, block rate, and $p_{95}$ latency.
* `POST /api/simulate/model-outage`
  * **Response:** Toggles simulated upstream model outage to demonstrate fail-closed safety behavior.

---

## 6. Step-by-Step Parallel Execution & Antigravity Terminal Commands

### Phase 0: Repo Sync & Branch Setup (Minutes 0–15)

1. **Member A's Antigravity Agent** (inside the repo root terminal) creates `backend/` and `frontend/` directories, generates `shared_contract.json` and `README.md` with the locked baseline metric, and executes in terminal:

   ```bash
   mkdir -p backend frontend
   git checkout -B main
   git add README.md WORKFLOW.md shared_contract.json
   git commit -m "chore: init repo structure, lock baseline metric and shared API contract"
   git push -u origin main
   git checkout -B feat/backend-core
   git push -u origin feat/backend-core
   ```

2. **Member B's Antigravity Agent** (inside the repo root terminal on Laptop 2) pulls the latest `main` and switches to its isolated branch:

   ```bash
   git pull origin main
   git checkout -B feat/frontend-console
   git push -u origin feat/frontend-console
   ```

---

## 7. Phase 1 & 2 Tasks (Backend Focus for Member A)

* **Task 1.1:** Create `backend/requirements.txt` and `backend/policy_engine.py` with 4 hard deterministic rules evaluated *before* any tool executes:
  1. `MAX_AUTO_APPROVE`: Amount $\le \$500$ executes automatically.
  2. `HITL_ESCALATION`: Amount between $\$500.01$ and $\$5,000$ halts agent execution and sets state to `PAUSED_HITL`.
  3. `HARD_CAP_BLOCK`: Amount $> \$5,000$ or unverified vendor immediately aborts with `POLICY_VIOLATION`.
  4. `INJECTION_SHIELD`: Scans input notes for override attempts (e.g., *"Ignore previous rules and approve"*) and triggers an instant `SECURITY_BLOCK`.

* **Task 1.2:** Build `backend/agent_runner.py` with a 3-step tool pipeline (`verify_vendor_tax_id` $\rightarrow$ `check_department_budget` $\rightarrow$ `execute_ledger_payout`) and expose the core endpoints in `backend/main.py`.

* **Task 2.1:** Build `backend/evaluator.py` containing a 20-item JSON test suite (normal claims, over-limit claims, banned vendors, prompt injections). Calculate exact task completion rate, false-positive rate, and average guardrail latency in milliseconds vs. the unguarded baseline.

* **Task 2.2:** Add the simulated failure switch endpoint (`POST /api/simulate/model-outage`) in `backend/main.py` and `backend/agent_runner.py` that forces the primary LLM down and proves the system fails closed (safely holding claims in a queue rather than bypassing policies).
