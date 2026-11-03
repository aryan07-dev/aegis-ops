"""Autonomous Multi-Step Procurement & Settlement Agent Runner.

Implements the 3-step tool execution pipeline:
1. verify_vendor_tax_id
2. check_department_budget
3. execute_ledger_payout

Guarded deterministically by PolicyEngine prior to executing privileged actions.
Supports Human-in-the-Loop (HITL) pause/resume and fail-closed model outage handling.
Enriched with human-friendly plain English summaries and 3-step UI milestones.
"""

from datetime import datetime, timezone
import hashlib
import time
from typing import Any, Dict, List, Optional
import uuid

from policy_engine import PolicyEngine, PolicyEvaluationResult

# Simulated Vendor Tax Registry
MOCK_VENDOR_TAX_REGISTRY: Dict[str, str] = {
    "aws cloud": "US-47-1982341",
    "amazon web services": "US-47-1982341",
    "microsoft azure": "US-91-0428172",
    "google cloud": "US-77-0293810",
    "slack technologies": "US-26-8819230",
    "slack": "US-26-8819230",
    "datadog": "US-13-4491028",
    "github": "US-27-0192847",
    "atlassian": "US-88-2910384",
    "zoom": "US-61-1928374",
    "figma": "US-45-9920192",
    "snowflake": "US-34-1182930",
    "stripe": "US-36-8192031",
    "twilio": "US-20-4491823",
    "apple": "US-94-2404110",
    "dell": "US-74-2489210",
    "jetbrains": "US-55-9283746",
    "notion": "US-82-1928374",
    "pagerduty": "US-27-3918273",
}

# In-memory audit trace database
TRACE_STORE: Dict[str, Dict[str, Any]] = {}

# Outage simulation flag (fail-closed demonstration)
SIMULATED_MODEL_OUTAGE: bool = False


def set_model_outage(enabled: bool) -> bool:
    global SIMULATED_MODEL_OUTAGE
    SIMULATED_MODEL_OUTAGE = enabled
    return SIMULATED_MODEL_OUTAGE


def get_model_outage() -> bool:
    return SIMULATED_MODEL_OUTAGE


class ProcurementAgent:
    """Multi-step procurement agent with deterministic pre-tool guardrails."""

    @staticmethod
    def verify_vendor_tax_id(vendor: str) -> Dict[str, Any]:
        """Tool 1: Verifies vendor tax registration and EIN."""
        norm = vendor.strip().lower()
        tax_id = MOCK_VENDOR_TAX_REGISTRY.get(norm)
        if tax_id:
            return {
                "status": "VERIFIED",
                "tax_id": tax_id,
                "vendor": vendor,
                "jurisdiction": "US-FEDERAL",
            }
        return {
            "status": "UNVERIFIED",
            "tax_id": None,
            "vendor": vendor,
            "error": "Vendor not found in corporate tax registry.",
        }

    @staticmethod
    def check_department_budget(category: str, amount: float) -> Dict[str, Any]:
        """Tool 2: Queries department ledger for budget allocations."""
        allocated = 50000.00
        consumed = 14320.00
        available = allocated - consumed
        sufficient = available >= amount
        return {
            "category": category,
            "allocated_budget": allocated,
            "consumed_budget": consumed,
            "available_budget": available,
            "amount_requested": amount,
            "budget_sufficient": sufficient,
        }

    @staticmethod
    def execute_ledger_payout(employee_id: str, vendor: str, amount: float, trace_id: str) -> Dict[str, Any]:
        """Tool 3: Executes double-entry general ledger payout."""
        raw_hash = f"{employee_id}:{vendor}:{amount}:{trace_id}:{time.time()}"
        tx_hash = "TX-LEDGER-" + hashlib.sha256(raw_hash.encode()).hexdigest()[:12].upper()
        return {
            "status": "SETTLED",
            "transaction_hash": tx_hash,
            "amount": amount,
            "currency": "USD",
            "payout_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def run_claim(cls, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrates claim execution through the policy engine and 3-step pipeline."""
        start_time = time.perf_counter()
        trace_id = f"trc_{uuid.uuid4().hex[:10]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        steps: List[Dict[str, Any]] = []

        # Step 0: Check upstream model outage simulation (fail-closed test)
        if SIMULATED_MODEL_OUTAGE:
            steps.append({
                "step_name": "MODEL_AVAILABILITY_CHECK",
                "status": "SIMULATED_OUTAGE_DETECTED",
                "details": "Upstream LLM connectivity unavailable. Enforcing FAIL-CLOSED safety protocol.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            steps.append({
                "step_name": "FAIL_CLOSED_CIRCUIT_BREAKER",
                "status": "TRIGGERED",
                "details": "Claim held in secure retry escrow. Zero financial settlement authorized during upstream outage.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            human_summary = "Held in Safe Queue — Upstream model unavailable; failing closed to prevent unauthorized payout."
            ui_steps = [
                {"label": "Vendor Registry", "status": "warning"},
                {"label": "Policy Guardrail", "status": "warning"},
                {"label": "Treasury Payout", "status": "paused"},
            ]
            trace_record = {
                "trace_id": trace_id,
                "timestamp": now_iso,
                "employee_id": claim.get("employee_id"),
                "vendor": claim.get("vendor"),
                "category": claim.get("category"),
                "amount": float(claim.get("amount", 0.0)),
                "notes": claim.get("notes"),
                "status": "FAILED_CLOSED",
                "policy_verdict": "BLOCKED",
                "policy_rule_triggered": "FAIL_CLOSED_OUTAGE_TRIP",
                "human_summary": human_summary,
                "ui_steps": ui_steps,
                "guardrail_latency_ms": 0.15,
                "total_latency_ms": round((time.perf_counter() - start_time) * 1000.0, 2),
                "claim": claim,
                "steps": steps,
                "review": None,
                "error": "Upstream model outage simulated. System failed closed securely.",
            }
            TRACE_STORE[trace_id] = trace_record
            return trace_record

        # Step 1: Pre-Tool Deterministic Policy Evaluation
        eval_result: PolicyEvaluationResult = PolicyEngine.evaluate(claim)
        guardrail_latency_ms = eval_result.latency_ms

        steps.append({
            "step_name": "POLICY_GUARDRAIL_INTERCEPTION",
            "status": eval_result.verdict,
            "rule": eval_result.rule_triggered,
            "details": eval_result.reason,
            "guardrail_latency_ms": round(guardrail_latency_ms, 3),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Policy Block: Immediately halt, zero tool calls permitted
        if eval_result.verdict == "BLOCKED":
            steps.append({
                "step_name": "EXECUTION_HALT",
                "status": "POLICY_VIOLATION",
                "details": f"Deterministic interception by {eval_result.rule_triggered}. Pre-empted all financial tools.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            total_latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            
            # Determine milestone status based on violation type
            if eval_result.rule_triggered == "INJECTION_SHIELD":
                vendor_status = "done"
            elif "unverified" in eval_result.reason.lower() or "blacklisted" in eval_result.reason.lower():
                vendor_status = "error"
            else:
                vendor_status = "done"

            ui_steps = [
                {"label": "Vendor Registry", "status": vendor_status},
                {"label": "Policy Guardrail", "status": "error"},
                {"label": "Treasury Payout", "status": "blocked"},
            ]

            trace_record = {
                "trace_id": trace_id,
                "timestamp": now_iso,
                "employee_id": claim.get("employee_id"),
                "vendor": claim.get("vendor"),
                "category": claim.get("category"),
                "amount": float(claim.get("amount", 0.0)),
                "notes": claim.get("notes"),
                "status": "BLOCKED",
                "policy_verdict": eval_result.verdict,
                "policy_rule_triggered": eval_result.rule_triggered,
                "human_summary": eval_result.human_summary,
                "ui_steps": ui_steps,
                "guardrail_latency_ms": round(guardrail_latency_ms, 3),
                "total_latency_ms": total_latency_ms,
                "claim": claim,
                "steps": steps,
                "review": None,
                "error": eval_result.reason,
            }
            TRACE_STORE[trace_id] = trace_record
            return trace_record

        # Tool 1: Verify vendor tax registry
        vendor = str(claim.get("vendor", ""))
        tax_res = cls.verify_vendor_tax_id(vendor)
        steps.append({
            "step_name": "TOOL_CALL:verify_vendor_tax_id",
            "status": tax_res["status"],
            "details": f"Vendor tax ID resolved: {tax_res.get('tax_id')}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Tool 2: Check department budget
        category = str(claim.get("category", "General"))
        amount = float(claim.get("amount", 0.0))
        budget_res = cls.check_department_budget(category, amount)
        steps.append({
            "step_name": "TOOL_CALL:check_department_budget",
            "status": "SUFFICIENT" if budget_res["budget_sufficient"] else "DEPLETED",
            "details": f"Remaining budget ${budget_res['available_budget']:,.2f} vs requested ${amount:,.2f}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # HITL Escalation: Pause execution before tool 3 (Ledger Payout)
        if eval_result.verdict == "PAUSED_HITL":
            steps.append({
                "step_name": "HITL_GATE_ESCALATION",
                "status": "PAUSED_HITL",
                "rule": eval_result.rule_triggered,
                "details": f"Transaction of ${amount:,.2f} paused for human supervisor review. Payout withheld.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            total_latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            ui_steps = [
                {"label": "Vendor Registry", "status": "done"},
                {"label": "Policy Guardrail", "status": "warning"},
                {"label": "Treasury Payout", "status": "paused"},
            ]
            trace_record = {
                "trace_id": trace_id,
                "timestamp": now_iso,
                "employee_id": claim.get("employee_id"),
                "vendor": claim.get("vendor"),
                "category": claim.get("category"),
                "amount": amount,
                "notes": claim.get("notes"),
                "status": "PAUSED_HITL",
                "policy_verdict": eval_result.verdict,
                "policy_rule_triggered": eval_result.rule_triggered,
                "human_summary": eval_result.human_summary,
                "ui_steps": ui_steps,
                "guardrail_latency_ms": round(guardrail_latency_ms, 3),
                "total_latency_ms": total_latency_ms,
                "claim": claim,
                "steps": steps,
                "review": None,
                "error": None,
            }
            TRACE_STORE[trace_id] = trace_record
            return trace_record

        # Auto-Approved: Execute Tool 3 (Ledger Payout)
        employee_id = str(claim.get("employee_id", "EMP-UNKNOWN"))
        payout_res = cls.execute_ledger_payout(employee_id, vendor, amount, trace_id)
        steps.append({
            "step_name": "TOOL_CALL:execute_ledger_payout",
            "status": payout_res["status"],
            "details": f"Settled payout via ledger ref {payout_res['transaction_hash']}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        total_latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        ui_steps = [
            {"label": "Vendor Registry", "status": "done"},
            {"label": "Policy Guardrail", "status": "done"},
            {"label": "Treasury Payout", "status": "done"},
        ]
        trace_record = {
            "trace_id": trace_id,
            "timestamp": now_iso,
            "employee_id": employee_id,
            "vendor": vendor,
            "category": category,
            "amount": amount,
            "notes": claim.get("notes"),
            "status": "COMPLETED",
            "policy_verdict": eval_result.verdict,
            "policy_rule_triggered": eval_result.rule_triggered,
            "human_summary": eval_result.human_summary,
            "ui_steps": ui_steps,
            "guardrail_latency_ms": round(guardrail_latency_ms, 3),
            "total_latency_ms": total_latency_ms,
            "claim": claim,
            "steps": steps,
            "review": None,
            "error": None,
        }
        TRACE_STORE[trace_id] = trace_record
        return trace_record

    @classmethod
    def approve_or_reject_claim(
        cls, trace_id: str, decision: str, reviewer_note: str = ""
    ) -> Dict[str, Any]:
        """Handles Human-In-The-Loop approval or rejection for paused claims."""
        trace = TRACE_STORE.get(trace_id)
        if not trace:
            return {
                "trace_id": trace_id,
                "status": "ERROR",
                "error": f"Trace {trace_id} not found in database.",
            }

        decision_upper = decision.strip().upper()

        if trace["status"] != "PAUSED_HITL":
            return {
                "trace_id": trace_id,
                "status": trace["status"],
                "message": f"Claim cannot be modified. Current status is {trace['status']}.",
                "human_summary": trace.get("human_summary", ""),
                "ui_steps": trace.get("ui_steps", []),
                "steps": trace.get("steps", []),
            }

        review_meta = {
            "decision": decision_upper,
            "reviewer_note": reviewer_note,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
        trace["review"] = review_meta

        if decision_upper == "APPROVE":
            # Resume and execute Tool 3 (Ledger Payout)
            employee_id = trace.get("employee_id", "EMP-UNKNOWN")
            vendor = trace.get("vendor", "UNKNOWN")
            amount = float(trace.get("amount", 0.0))
            payout_res = cls.execute_ledger_payout(employee_id, vendor, amount, trace_id)

            trace["steps"].append({
                "step_name": "HITL_HUMAN_OVERRIDE",
                "status": "APPROVED",
                "details": f"Human Supervisor Authorized: {reviewer_note or 'Approved via Console'}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            trace["steps"].append({
                "step_name": "TOOL_CALL:execute_ledger_payout",
                "status": payout_res["status"],
                "details": f"Resumed & Settled payout via ledger ref {payout_res['transaction_hash']}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            trace["status"] = "COMPLETED"
            human_summary = "Approved by Manager — Override granted; treasury payout settled."
            ui_steps = [
                {"label": "Vendor Registry", "status": "done"},
                {"label": "Policy Guardrail", "status": "warning"},
                {"label": "Treasury Payout", "status": "done"},
            ]
            trace["human_summary"] = human_summary
            trace["ui_steps"] = ui_steps

            return {
                "trace_id": trace_id,
                "status": "COMPLETED",
                "policy_verdict": "PASSED_WITH_HITL_OVERRIDE",
                "human_summary": human_summary,
                "ui_steps": ui_steps,
                "reviewer_note": reviewer_note,
                "message": "Claim successfully approved and ledger payout dispatched.",
                "steps": trace["steps"],
            }
        else:
            trace["steps"].append({
                "step_name": "HITL_HUMAN_REJECTION",
                "status": "REJECTED",
                "details": f"Human Supervisor Rejected: {reviewer_note or 'Rejected via Console'}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            trace["status"] = "REJECTED"
            human_summary = "Rejected by Manager — Claim terminated by supervisor; funds withheld."
            ui_steps = [
                {"label": "Vendor Registry", "status": "done"},
                {"label": "Policy Guardrail", "status": "warning"},
                {"label": "Treasury Payout", "status": "blocked"},
            ]
            trace["human_summary"] = human_summary
            trace["ui_steps"] = ui_steps

            return {
                "trace_id": trace_id,
                "status": "REJECTED",
                "policy_verdict": "REJECTED_BY_HUMAN",
                "human_summary": human_summary,
                "ui_steps": ui_steps,
                "reviewer_note": reviewer_note,
                "message": "Claim rejected by human supervisor. Funds withheld.",
                "steps": trace["steps"],
            }
