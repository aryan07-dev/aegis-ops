"""FastAPI Backend Server for Aegis-Ops Governance Engine.

Provides REST endpoints for:
- Autonomous claim execution with pre-tool policy guardrails & Nova Act simulation
- Audit trace history and live telemetry with plain-English summaries & UI milestones
- Human-in-the-Loop (HITL) approval actions
- Fail-closed upstream outage simulation
- 20-case evaluation benchmark runner
- Amazon Bedrock & AgentCore telemetry status (/api/aws/status)
- Realistic initial seed state for immediate dashboard readiness
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent_runner import (
    ProcurementAgent,
    TRACE_STORE,
    set_model_outage,
    get_model_outage,
)
from evaluator import BenchmarkEvaluator

app = FastAPI(
    title="Aegis-Ops Governance Engine API",
    description="Autonomous procurement & expense claim settlement agent with Amazon AgentCore deterministic guardrails and Nova Act automation.",
    version="1.2.0",
)

# CORS configuration for frontend operator console
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_initial_state() -> None:
    """Pre-populates 2 realistic initial claims for clean and alive dashboard presentation."""
    if not TRACE_STORE:
        # Claim 1: Auto-approved $280 Datadog invoice (Autonomous Nova Act & Ledger settlement)
        ProcurementAgent.run_claim({
            "employee_id": "EMP-102",
            "vendor": "Datadog",
            "category": "Monitoring",
            "amount": 280.00,
            "notes": "Monthly APM infrastructure monitoring and synthetic trace ingestion",
        })
        # Claim 2: Paused $1,450 MacBook Pro purchase awaiting supervisor sign-off
        ProcurementAgent.run_claim({
            "employee_id": "EMP-304",
            "vendor": "Apple",
            "category": "Hardware",
            "amount": 1450.00,
            "notes": "MacBook Pro M3 upgrade for engineering workstation",
        })


# Populate seed data immediately upon module import
seed_initial_state()


@app.on_event("startup")
def on_startup():
    seed_initial_state()


class ClaimRequest(BaseModel):
    employee_id: str = Field(..., example="EMP-402")
    vendor: str = Field(..., example="AWS Cloud")
    category: str = Field(..., example="Infrastructure")
    amount: float = Field(..., example=420.00)
    notes: str = Field(..., example="Q3 Server Cluster")


class ApprovalRequest(BaseModel):
    decision: str = Field(..., example="APPROVE")
    reviewer_note: Optional[str] = Field(default="", example="Verified with VP")


class OutageSimulationRequest(BaseModel):
    enabled: Optional[bool] = None


@app.get("/")
def read_root():
    return {
        "system": "aegis-ops",
        "service": "Autonomous Enterprise Governance & Intervention System",
        "status": "OPERATIONAL",
        "cloud_provider": "Amazon Web Services (AWS)",
        "region": "us-east-1",
        "bedrock_model": "anthropic.claude-3-5-sonnet",
        "agentcore_status": "ACTIVE",
        "nova_act_status": "READY",
        "model_outage_simulated": get_model_outage(),
        "active_traces_count": len(TRACE_STORE),
    }


@app.get("/api/aws/status")
def get_aws_status():
    """Returns simulated AWS Bedrock, AgentCore, and Nova Act environment telemetry."""
    outage_active = get_model_outage()
    return {
        "region": "us-east-1",
        "bedrock_model": "anthropic.claude-3-5-sonnet",
        "bedrock_fallback_model": "amazon.nova-pro-v1",
        "agentcore_status": "DEGRADED_FAIL_CLOSED" if outage_active else "ACTIVE",
        "agentcore_version": "2026.3.0",
        "nova_act_status": "PAUSED" if outage_active else "READY",
        "nova_act_browser_engine": "chromium-headless-aws-lambda",
        "guardrail_arn": "arn:aws:bedrock:us-east-1:123456789012:guardrail/aegis-procure-policy",
        "latency_sla": "< 15ms deterministic guardrail overhead",
        "fail_closed_mode": "STRICT_FAIL_CLOSED",
        "cloudwatch_telemetry": "CONNECTED",
        "active_sessions": len(TRACE_STORE),
    }


@app.post("/api/claims/run", status_code=status.HTTP_200_OK)
def run_claim(claim: ClaimRequest):
    """Executes an employee claim through the autonomous multi-step reasoning and guardrail loop."""
    result = ProcurementAgent.run_claim(claim.model_dump())
    return result


@app.get("/api/claims/traces", response_model=List[Dict[str, Any]])
def get_traces():
    """Returns chronological audit trace log of all claims with human summaries and ui_steps."""
    traces = list(TRACE_STORE.values())
    return sorted(traces, key=lambda t: t.get("timestamp", ""), reverse=True)


@app.get("/api/claims/{trace_id}")
def get_trace_by_id(trace_id: str):
    """Fetches full execution trace by ID."""
    trace = TRACE_STORE.get(trace_id)
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace ID '{trace_id}' not found.",
        )
    return trace


@app.post("/api/claims/{trace_id}/approve")
def approve_claim(trace_id: str, request: ApprovalRequest):
    """Submits Human-In-The-Loop review (APPROVE / REJECT) to resume or abort paused runs."""
    result = ProcurementAgent.approve_or_reject_claim(
        trace_id=trace_id,
        decision=request.decision,
        reviewer_note=request.reviewer_note or "",
    )
    if result.get("status") == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error"),
        )
    return result


@app.get("/api/simulate/model-outage")
def get_outage_status():
    """Returns current upstream outage simulation state."""
    active = get_model_outage()
    return {
        "model_outage_simulated": active,
        "status": "FAIL_CLOSED_ACTIVE" if active else "NORMAL_OPERATION",
    }


@app.post("/api/simulate/model-outage")
def toggle_model_outage(request: Optional[OutageSimulationRequest] = None):
    """Toggles upstream LLM outage simulation to demonstrate deterministic fail-closed safety."""
    current = get_model_outage()
    new_state = (not current) if (request is None or request.enabled is None) else request.enabled
    set_model_outage(new_state)
    return {
        "model_outage_simulated": new_state,
        "status": "FAIL_CLOSED_ACTIVE" if new_state else "NORMAL_OPERATION",
        "message": "Upstream LLM outage simulated. System fails closed and withholds ledger settlement."
        if new_state
        else "Upstream LLM connectivity restored. Normal operations resumed.",
    }


@app.get("/api/eval/run")
def run_evaluation_suite():
    """Runs the 20-case adversarial benchmark suite comparing baseline vs governed agent."""
    return BenchmarkEvaluator.run_suite()
