"""Autonomous Multi-Step Procurement & Settlement Agent Runner.

Implements an autonomous multi-step reasoning and dynamic tool execution loop:
1. Dynamic Intent Formulation & Execution Planning
2. Tool 1: fetch_vendor_registry (external registry query)
3. Tool 2: evaluate_agentcore_policy (Amazon Bedrock & AgentCore policy guardrail)
4. Dynamic Branching:
   - Immediate Halt on Security/Policy Block
   - Autonomous Pause on HITL Escalation ($500.01 - $5,000)
   - Tool 3: trigger_nova_act_browser & execute_ledger_payout on Instant Auto-Approval
5. Resume capabilities upon human manager sign-off.
"""

from datetime import datetime, timezone
import hashlib
import time
from typing import Any, Dict, List, Optional
import uuid

from policy_engine import PolicyEngine, PolicyEvaluationResult

# Simulated Vendor Tax Registry
MOCK_VENDOR_TAX_REGISTRY: Dict[str, Dict[str, Any]] = {
    "aws cloud": {"tax_id": "US-47-1982341", "tier": "ENTERPRISE_STRATEGIC", "verified": True},
    "amazon web services": {"tax_id": "US-47-1982341", "tier": "ENTERPRISE_STRATEGIC", "verified": True},
    "microsoft azure": {"tax_id": "US-91-0428172", "tier": "ENTERPRISE_PREFERRED", "verified": True},
    "google cloud": {"tax_id": "US-77-0293810", "tier": "ENTERPRISE_PREFERRED", "verified": True},
    "slack technologies": {"tax_id": "US-26-8819230", "tier": "ENTERPRISE_STANDARD", "verified": True},
    "slack": {"tax_id": "US-26-8819230", "tier": "ENTERPRISE_STANDARD", "verified": True},
    "datadog": {"tax_id": "US-13-4491028", "tier": "ENTERPRISE_PREFERRED", "verified": True},
    "github": {"tax_id": "US-27-0192847", "tier": "ENTERPRISE_STRATEGIC", "verified": True},
    "atlassian": {"tax_id": "US-88-2910384", "tier": "ENTERPRISE_STANDARD", "verified": True},
    "zoom": {"tax_id": "US-61-1928374", "tier": "ENTERPRISE_STANDARD", "verified": True},
    "figma": {"tax_id": "US-45-9920192", "tier": "ENTERPRISE_STANDARD", "verified": True},
    "snowflake": {"tax_id": "US-34-1182930", "tier": "ENTERPRISE_PREFERRED", "verified": True},
    "stripe": {"tax_id": "US-36-8192031", "tier": "ENTERPRISE_STRATEGIC", "verified": True},
    "twilio": {"tax_id": "US-20-4491823", "tier": "ENTERPRISE_STANDARD", "verified": True},
    "apple": {"tax_id": "US-94-2404110", "tier": "HARDWARE_OEM_CERTIFIED", "verified": True},
    "dell": {"tax_id": "US-74-2489210", "tier": "HARDWARE_OEM_CERTIFIED", "verified": True},
    "jetbrains": {"tax_id": "US-55-9283746", "tier": "ENTERPRISE_STANDARD", "verified": True},
    "notion": {"tax_id": "US-82-1928374", "tier": "ENTERPRISE_STANDARD", "verified": True},
    "pagerduty": {"tax_id": "US-27-3918273", "tier": "ENTERPRISE_STANDARD", "verified": True},
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
    """Autonomous agent engine with Amazon Bedrock & AgentCore design patterns."""

    @staticmethod
    def fetch_vendor_registry(vendor: str) -> Dict[str, Any]:
        """Tool 1: Dynamic lookup in enterprise vendor registry."""
        norm = vendor.strip().lower()
        rec = MOCK_VENDOR_TAX_REGISTRY.get(norm)
        if rec and rec["verified"]:
            return {
                "status": "VERIFIED",
                "tax_id": rec["tax_id"],
                "tier": rec["tier"],
                "vendor": vendor,
                "registry": "AWS-DYNAMODB-GLOBAL-VENDOR-REGISTRY",
                "jurisdiction": "US-FEDERAL",
            }
        return {
            "status": "UNVERIFIED",
            "tax_id": None,
            "tier": "UNVERIFIED_THIRD_PARTY",
            "vendor": vendor,
            "error": "Vendor not found in corporate vendor registry.",
        }

    # Backward compatibility alias
    verify_vendor_tax_id = fetch_vendor_registry

    @staticmethod
    def evaluate_agentcore_policy(claim: Dict[str, Any]) -> PolicyEvaluationResult:
        """Tool 2: Evaluates Amazon AgentCore deterministic pre-tool guardrails."""
        return PolicyEngine.evaluate(claim)

    @staticmethod
    def check_department_budget(category: str, amount: float) -> Dict[str, Any]:
        """Auxiliary Tool: Ledger budget verification."""
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
    def trigger_nova_act_browser(
        employee_id: str, vendor: str, amount: float, trace_id: str, action: str = "submit_and_settle"
    ) -> Dict[str, Any]:
        """Tool 3A: Simulates Amazon Nova Act headless browser workflow automation.

        Automates Coupa/SAP ERP procurement portal interaction, invoice reconciliation,
        and automated settlement certificate generation.
        """
        session_id = f"nova-act-ses-{uuid.uuid4().hex[:8]}"
        return {
            "status": "AUTOMATED_VIA_NOVA_ACT",
            "session_id": session_id,
            "browser_engine": "chromium-headless-aws-lambda",
            "target_portal": "Coupa Enterprise Financial Cloud",
            "action_executed": action,
            "vendor": vendor,
            "reconciliation_amount": amount,
            "automated_audit_url": f"https://console.aws.amazon.com/nova-act/sessions/{session_id}",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def execute_ledger_payout(employee_id: str, vendor: str, amount: float, trace_id: str) -> Dict[str, Any]:
        """Tool 3B: Executes double-entry general ledger payout."""
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
        """Executes an autonomous multi-step reasoning and dynamic tool execution loop."""
        start_time = time.perf_counter()
        trace_id = f"trc_{uuid.uuid4().hex[:10]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        vendor = str(claim.get("vendor", "")).strip()
        category = str(claim.get("category", "General")).strip()
        amount = float(claim.get("amount", 0.0))
        employee_id = str(claim.get("employee_id", "EMP-UNKNOWN")).strip()
        notes = str(claim.get("notes", "")).strip()

        steps: List[Dict[str, Any]] = []

        # Step 0: Autonomous LLM availability check (Fail-Closed handling)
        if SIMULATED_MODEL_OUTAGE:
            steps.append({
                "step_name": "AGENT_REASONING: MODEL_CONNECTIVITY_PROBE",
                "status": "FAIL_CLOSED_INTERVENTION",
                "details": "Amazon Bedrock endpoint unreachable (simulated outage). Triggering fail-closed escrow protocol.",
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
                "employee_id": employee_id,
                "vendor": vendor,
                "category": category,
                "amount": amount,
                "notes": notes,
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
                "agentcore_policy_id": "policy-sec-model-outage-fail-closed",
                "risk_score": 0.50,
                "evaluation_score": 0.00,
            }
            TRACE_STORE[trace_id] = trace_record
            return trace_record

        # Step 1: Autonomous Plan Formulation
        steps.append({
            "step_name": "AGENT_REASONING: Formulating Autonomous Execution Plan",
            "status": "PLANNED",
            "details": f"Analyzing procurement claim for '{vendor}' (${amount:,.2f}). Planned dynamic sequence: 1. fetch_vendor_registry -> 2. evaluate_agentcore_policy -> 3. trigger_nova_act_browser & ledger settlement.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Step 2: Dynamic Tool Execution 1 — fetch_vendor_registry
        tax_res = cls.fetch_vendor_registry(vendor)
        vendor_status = tax_res.get("status")
        steps.append({
            "step_name": "TOOL_CALL:fetch_vendor_registry",
            "status": vendor_status,
            "details": f"Registry match: EIN {tax_res.get('tax_id', 'N/A')} (Tier: {tax_res.get('tier', 'N/A')})",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Step 3: Dynamic Tool Execution 2 — evaluate_agentcore_policy
        eval_result: PolicyEvaluationResult = cls.evaluate_agentcore_policy(claim)
        guardrail_latency_ms = eval_result.latency_ms

        steps.append({
            "step_name": "TOOL_CALL:evaluate_agentcore_policy",
            "status": eval_result.verdict,
            "rule": eval_result.rule_triggered,
            "details": f"Amazon AgentCore Policy [{eval_result.agentcore_policy_id}] Verdict: {eval_result.verdict} (Risk: {eval_result.risk_score}, Conf: {eval_result.confidence_metric}) - {eval_result.reason}",
            "guardrail_latency_ms": round(guardrail_latency_ms, 3),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Branch A: Security / Policy Block — Autonomous Termination
        if eval_result.verdict == "BLOCKED":
            steps.append({
                "step_name": "AGENT_ACTION: Terminate Autonomous Run",
                "status": "POLICY_VIOLATION",
                "details": f"Deterministic interception by {eval_result.rule_triggered} ({eval_result.agentcore_policy_id}). Pre-empted all downstream financial tools.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            total_latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

            ui_vendor_status = "done"
            if "unverified" in eval_result.reason.lower() or "blacklisted" in eval_result.reason.lower():
                ui_vendor_status = "error"

            ui_steps = [
                {"label": "Vendor Registry", "status": ui_vendor_status},
                {"label": "Policy Guardrail", "status": "error"},
                {"label": "Treasury Payout", "status": "blocked"},
            ]

            trace_record = {
                "trace_id": trace_id,
                "timestamp": now_iso,
                "employee_id": employee_id,
                "vendor": vendor,
                "category": category,
                "amount": amount,
                "notes": notes,
                "status": "BLOCKED",
                "policy_verdict": eval_result.verdict,
                "policy_rule_triggered": eval_result.rule_triggered,
                "agentcore_policy_id": eval_result.agentcore_policy_id,
                "evaluation_score": eval_result.evaluation_score,
                "risk_score": eval_result.risk_score,
                "confidence_metric": eval_result.confidence_metric,
                "policy_arn": eval_result.policy_arn,
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

        # Auxiliary Budget check
        budget_res = cls.check_department_budget(category, amount)
        steps.append({
            "step_name": "TOOL_CALL:check_department_budget",
            "status": "SUFFICIENT" if budget_res["budget_sufficient"] else "DEPLETED",
            "details": f"Remaining budget ${budget_res['available_budget']:,.2f} vs requested ${amount:,.2f}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Branch B: HITL Escalation — Autonomous Pause & Context Preservation
        if eval_result.verdict == "PAUSED_HITL":
            steps.append({
                "step_name": "AGENT_DECISION: Autonomously Suspend for Human Review",
                "status": "PAUSED_HITL",
                "rule": eval_result.rule_triggered,
                "details": f"Amount ${amount:,.2f} falls into managerial oversight tier ($500.01 - $5,000.00). State preserved in AgentCore registry.",
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
                "employee_id": employee_id,
                "vendor": vendor,
                "category": category,
                "amount": amount,
                "notes": notes,
                "status": "PAUSED_HITL",
                "policy_verdict": eval_result.verdict,
                "policy_rule_triggered": eval_result.rule_triggered,
                "agentcore_policy_id": eval_result.agentcore_policy_id,
                "evaluation_score": eval_result.evaluation_score,
                "risk_score": eval_result.risk_score,
                "confidence_metric": eval_result.confidence_metric,
                "policy_arn": eval_result.policy_arn,
                "human_summary": eval_result.human_summary,
                "ui_steps": ui_steps,
                "guardrail_latency_ms": round(guardrail_latency_ms, 3),
                "total_latency_ms": total_latency_ms,
                "claim": claim,
                "steps": steps,
                "review": None,
                "error": None,
                "agent_context": {
                    "next_step": "trigger_nova_act_browser",
                    "vendor_tax_id": tax_res.get("tax_id"),
                },
            }
            TRACE_STORE[trace_id] = trace_record
            return trace_record

        # Branch C: Auto-Approval — Dynamic Tool 3 Execution (Nova Act Browser + Ledger Payout)
        steps.append({
            "step_name": "AGENT_REASONING: Dispatching Automated Settlement",
            "status": "DISPATCHING",
            "details": f"Autonomous settlement authorized (< $500). Launching Nova Act browser automation for Coupa enterprise portal.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        nova_res = cls.trigger_nova_act_browser(employee_id, vendor, amount, trace_id)
        steps.append({
            "step_name": "TOOL_CALL:trigger_nova_act_browser",
            "status": nova_res["status"],
            "details": f"Nova Act session [{nova_res['session_id']}] automated Coupa portal claim submission.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        payout_res = cls.execute_ledger_payout(employee_id, vendor, amount, trace_id)
        steps.append({
            "step_name": "TOOL_CALL:execute_ledger_payout",
            "status": payout_res["status"],
            "details": f"Double-entry settlement sealed via ledger ref {payout_res['transaction_hash']}",
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
            "notes": notes,
            "status": "COMPLETED",
            "policy_verdict": eval_result.verdict,
            "policy_rule_triggered": eval_result.rule_triggered,
            "agentcore_policy_id": eval_result.agentcore_policy_id,
            "evaluation_score": eval_result.evaluation_score,
            "risk_score": eval_result.risk_score,
            "confidence_metric": eval_result.confidence_metric,
            "policy_arn": eval_result.policy_arn,
            "human_summary": eval_result.human_summary,
            "ui_steps": ui_steps,
            "guardrail_latency_ms": round(guardrail_latency_ms, 3),
            "total_latency_ms": total_latency_ms,
            "claim": claim,
            "steps": steps,
            "review": None,
            "error": None,
            "nova_act_session_id": nova_res["session_id"],
        }
        TRACE_STORE[trace_id] = trace_record
        return trace_record

    @classmethod
    def approve_or_reject_claim(
        cls, trace_id: str, decision: str, reviewer_note: str = ""
    ) -> Dict[str, Any]:
        """Resumes paused autonomous agent execution upon human manager action."""
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
            employee_id = trace.get("employee_id", "EMP-UNKNOWN")
            vendor = trace.get("vendor", "UNKNOWN")
            amount = float(trace.get("amount", 0.0))

            trace["steps"].append({
                "step_name": "AGENT_RESUME: Human Manager Authorization Received",
                "status": "RESUMED",
                "details": f"Manager sign-off confirmed: '{reviewer_note or 'Approved via Console'}'. Resuming autonomous tool execution pipeline.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            # Execute Tool 3A: Nova Act Browser Workflow
            nova_res = cls.trigger_nova_act_browser(employee_id, vendor, amount, trace_id, action="manager_override_reconciliation")
            trace["steps"].append({
                "step_name": "TOOL_CALL:trigger_nova_act_browser",
                "status": nova_res["status"],
                "details": f"Resumed Nova Act session [{nova_res['session_id']}] for manager-authorized portal reconciliation.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            # Execute Tool 3B: Double-Entry Ledger Payout
            payout_res = cls.execute_ledger_payout(employee_id, vendor, amount, trace_id)
            trace["steps"].append({
                "step_name": "TOOL_CALL:execute_ledger_payout",
                "status": payout_res["status"],
                "details": f"Settled payout via ledger ref {payout_res['transaction_hash']}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            human_summary = "Approved by Manager — Override granted; treasury payout settled."
            ui_steps = [
                {"label": "Vendor Registry", "status": "done"},
                {"label": "Policy Guardrail", "status": "warning"},
                {"label": "Treasury Payout", "status": "done"},
            ]
            trace["status"] = "COMPLETED"
            trace["human_summary"] = human_summary
            trace["ui_steps"] = ui_steps
            trace["nova_act_session_id"] = nova_res["session_id"]

            return {
                "trace_id": trace_id,
                "status": "COMPLETED",
                "policy_verdict": "PASSED_WITH_HITL_OVERRIDE",
                "human_summary": human_summary,
                "ui_steps": ui_steps,
                "reviewer_note": reviewer_note,
                "message": "Claim successfully approved, Nova Act reconciled, and ledger payout dispatched.",
                "steps": trace["steps"],
            }
        else:
            trace["steps"].append({
                "step_name": "AGENT_ABORT: Human Manager Rejection Received",
                "status": "TERMINATED",
                "details": f"Supervisor rejected claim: '{reviewer_note or 'Rejected via Console'}'. Autonomous run terminated, funds withheld.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            human_summary = "Rejected by Manager — Claim terminated by supervisor; funds withheld."
            ui_steps = [
                {"label": "Vendor Registry", "status": "done"},
                {"label": "Policy Guardrail", "status": "warning"},
                {"label": "Treasury Payout", "status": "blocked"},
            ]
            trace["status"] = "REJECTED"
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
