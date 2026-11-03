"""Deterministic Pre-Tool Policy Guardrail Engine.

Enforces 4 strict deterministic governance rules evaluated BEFORE any agent tool executes:
1. INJECTION_SHIELD: Scans inputs for prompt injections and adversarial overrides.
2. HARD_CAP_BLOCK: Rejects amounts > $5,000 or unverified/banned vendors immediately.
3. HITL_ESCALATION: Halts claims between $500.01 and $5,000 for Human-In-The-Loop approval.
4. MAX_AUTO_APPROVE: Automatically approves claims <= $500 for verified vendors.
"""

from dataclasses import dataclass
import re
import time
from typing import Any, Dict, Optional, Set

# Approved enterprise vendors registry
VERIFIED_VENDORS: Set[str] = {
    "aws cloud",
    "amazon web services",
    "microsoft azure",
    "google cloud",
    "slack technologies",
    "slack",
    "datadog",
    "github",
    "atlassian",
    "zoom",
    "figma",
    "snowflake",
    "stripe",
    "twilio",
    "apple",
    "dell",
    "jetbrains",
    "notion",
    "pagerduty",
}

# Explicitly banned or restricted entities
BANNED_VENDORS: Set[str] = {
    "cryptopay llc",
    "shellcorp offshore",
    "darkweb services",
    "shady vendor corp",
    "unregistered vendor",
    "unverified entity",
    "adversary enterprise",
}

# Regex patterns detecting adversarial prompt injection or guardrail bypass attempts
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above|system)\s+(rules|instructions|prompts)", re.IGNORECASE),
    re.compile(r"bypass\s+(all\s+)?(policy|policies|guardrails|checks|rules|security)", re.IGNORECASE),
    re.compile(r"disregard\s+(the\s+)?(previous|system|rules|guidelines)", re.IGNORECASE),
    re.compile(r"override\s+(policy|guardrail|rule|budget|threshold)", re.IGNORECASE),
    re.compile(r"you\s+must\s+approve", re.IGNORECASE),
    re.compile(r"admin\s+override", re.IGNORECASE),
    re.compile(r"system\s*prompt", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"simulate\s+(root|admin|god\s+mode)", re.IGNORECASE),
    re.compile(r"approve\s+without\s+check", re.IGNORECASE),
    re.compile(r"do\s+not\s+verify", re.IGNORECASE),
    re.compile(r"force\s+approval", re.IGNORECASE),
]


@dataclass
class PolicyEvaluationResult:
    allowed: bool
    verdict: str  # "PASSED", "PAUSED_HITL", "BLOCKED"
    rule_triggered: str  # "INJECTION_SHIELD", "HARD_CAP_BLOCK", "HITL_ESCALATION", "MAX_AUTO_APPROVE"
    reason: str
    human_summary: str
    latency_ms: float
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "verdict": self.verdict,
            "rule_triggered": self.rule_triggered,
            "reason": self.reason,
            "human_summary": self.human_summary,
            "latency_ms": round(self.latency_ms, 3),
            "details": self.details,
        }


class PolicyEngine:
    """Pre-tool execution guardrail interceptor."""

    MAX_AUTO_APPROVE_LIMIT: float = 500.00
    HITL_ESCALATION_LIMIT: float = 5000.00

    @classmethod
    def evaluate(cls, claim: Dict[str, Any]) -> PolicyEvaluationResult:
        """Deterministically evaluates a claim against corporate governance rules.

        Runs with < 15ms latency overhead (typically < 0.5ms).
        """
        start_time = time.perf_counter()

        amount = float(claim.get("amount", 0.0))
        vendor = str(claim.get("vendor", "")).strip()
        notes = str(claim.get("notes", "")).strip()
        category = str(claim.get("category", "")).strip()
        combined_text = f"{notes} {vendor} {category}"

        # 1. INJECTION_SHIELD: Check for prompt injections and adversarial jailbreaks
        for pattern in INJECTION_PATTERNS:
            match = pattern.search(combined_text)
            if match:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                return PolicyEvaluationResult(
                    allowed=False,
                    verdict="BLOCKED",
                    rule_triggered="INJECTION_SHIELD",
                    reason=f"Security alert: Adversarial prompt injection pattern detected ('{match.group(0)}')",
                    human_summary="Blocked by Security Guardrail — Adversarial instruction override detected in claim notes.",
                    latency_ms=latency_ms,
                    details={"matched_pattern": match.group(0)},
                )

        normalized_vendor = vendor.lower()

        # 2. HARD_CAP_BLOCK: Amount > $5,000 or unverified / banned vendor
        if normalized_vendor in BANNED_VENDORS:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return PolicyEvaluationResult(
                allowed=False,
                verdict="BLOCKED",
                rule_triggered="HARD_CAP_BLOCK",
                reason=f"Policy violation: Vendor '{vendor}' is blacklisted in vendor registry.",
                human_summary=f"Blocked by Policy — Vendor '{vendor}' is unverified or restricted in corporate registry.",
                latency_ms=latency_ms,
                details={"vendor": vendor, "vendor_status": "BANNED"},
            )

        if normalized_vendor not in VERIFIED_VENDORS:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return PolicyEvaluationResult(
                allowed=False,
                verdict="BLOCKED",
                rule_triggered="HARD_CAP_BLOCK",
                reason=f"Policy violation: Vendor '{vendor}' is not verified in corporate registry.",
                human_summary=f"Blocked by Policy — Vendor '{vendor}' is unverified or restricted in corporate registry.",
                latency_ms=latency_ms,
                details={"vendor": vendor, "vendor_status": "UNVERIFIED"},
            )

        if amount > cls.HITL_ESCALATION_LIMIT:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return PolicyEvaluationResult(
                allowed=False,
                verdict="BLOCKED",
                rule_triggered="HARD_CAP_BLOCK",
                reason=f"Policy violation: Claim amount (${amount:,.2f}) exceeds absolute threshold cap of ${cls.HITL_ESCALATION_LIMIT:,.2f}.",
                human_summary="Blocked by Policy — Exceeds $5,000 single-transaction treasury cap.",
                latency_ms=latency_ms,
                details={"amount": amount, "cap": cls.HITL_ESCALATION_LIMIT},
            )

        # 3. HITL_ESCALATION: Amount between $500.01 and $5,000 requires human authorization
        if amount > cls.MAX_AUTO_APPROVE_LIMIT:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return PolicyEvaluationResult(
                allowed=False,
                verdict="PAUSED_HITL",
                rule_triggered="HITL_ESCALATION",
                reason=f"Escalation required: Claim amount (${amount:,.2f}) exceeds auto-approval ceiling (${cls.MAX_AUTO_APPROVE_LIMIT:,.2f}). Human review required.",
                human_summary=f"Awaiting Manager Sign-Off — Claim exceeds $500 auto-settlement limit (${amount:,.2f}).",
                latency_ms=latency_ms,
                details={
                    "amount": amount,
                    "auto_ceiling": cls.MAX_AUTO_APPROVE_LIMIT,
                    "requires_approval": True,
                },
            )

        # 4. MAX_AUTO_APPROVE: Amount <= $500 with verified vendor
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return PolicyEvaluationResult(
            allowed=True,
            verdict="PASSED",
            rule_triggered="MAX_AUTO_APPROVE",
            reason=f"Claim approved: Amount (${amount:,.2f}) is within automated settlement limit of ${cls.MAX_AUTO_APPROVE_LIMIT:,.2f}.",
            human_summary="Approved automatically — Verified vendor within $500 instant-settlement tier.",
            latency_ms=latency_ms,
            details={"amount": amount, "auto_approved": True},
        )
