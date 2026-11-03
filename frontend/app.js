/**
 * AEGIS-OPS: INDUSTRIAL GOVERNANCE & EXECUTION CONSOLE
 * App Logic: Live Trace Renderer, Policy Gate Interceptor, & HITL Queue
 */

(function () {
  'use strict';

  // API Gateway URL
  const BACKEND_URL = 'http://localhost:8000';

  // DOM Elements
  const systemStatusDot = document.getElementById('system-status-dot');
  const systemStatusText = document.getElementById('system-status-text');
  const failClosedIndicator = document.getElementById('fail-closed-indicator');

  const claimForm = document.getElementById('claim-form');
  const claimEmp = document.getElementById('claim-emp');
  const claimVendor = document.getElementById('claim-vendor');
  const claimCategory = document.getElementById('claim-category');
  const claimAmount = document.getElementById('claim-amount');
  const claimNotes = document.getElementById('claim-notes');
  const btnSubmitClaim = document.getElementById('btn-submit-claim');

  const activeTraceIdEl = document.getElementById('active-trace-id');
  const activeTraceVerdictEl = document.getElementById('active-trace-verdict');
  const activeTraceLatencyEl = document.getElementById('active-trace-latency');
  const activeTraceStepsEl = document.getElementById('active-trace-steps');

  const stepNode1 = document.getElementById('step-node-1');
  const stepBadge1 = document.getElementById('step-badge-1');
  const stepNode2 = document.getElementById('step-node-2');
  const stepBadge2 = document.getElementById('step-badge-2');
  const stepNode3 = document.getElementById('step-node-3');
  const stepBadge3 = document.getElementById('step-badge-3');

  const traceLogContainer = document.getElementById('trace-log-container');
  const rawJsonOutput = document.getElementById('raw-json-output');
  const btnCopyJson = document.getElementById('btn-copy-json');

  const hitlQueueCount = document.getElementById('hitl-queue-count');
  const hitlEmptyMsg = document.getElementById('hitl-empty-msg');
  const hitlActiveCard = document.getElementById('hitl-active-card');
  const hitlClaimId = document.getElementById('hitl-claim-id');
  const hitlClaimEmp = document.getElementById('hitl-claim-emp');
  const hitlClaimAmount = document.getElementById('hitl-claim-amount');
  const hitlClaimRule = document.getElementById('hitl-claim-rule');
  const hitlReviewerNote = document.getElementById('hitl-reviewer-note');
  const btnHitlApprove = document.getElementById('btn-hitl-approve');
  const btnHitlReject = document.getElementById('btn-hitl-reject');

  const metricChecksCount = document.getElementById('metric-checks-count');
  const metricLatency = document.getElementById('metric-latency');

  // State
  let currentActiveTrace = null;
  let activePendingHitlTrace = null;
  let enforcedChecksCounter = 0;
  let isBackendLive = false;

  // Format timestamp helper: [HH:mm:ss.SSS]
  function getTimestamp() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    const ms = String(now.getMilliseconds()).padStart(3, '0');
    return `[${h}:${m}:${s}.${ms}]`;
  }

  // Append monospace log entry
  function appendLog(tag, tagType, message) {
    const entry = document.createElement('div');
    entry.className = 'log-entry';

    const timeSpan = document.createElement('span');
    timeSpan.className = 'log-timestamp';
    timeSpan.textContent = getTimestamp();

    const tagSpan = document.createElement('span');
    tagSpan.className = `log-tag tag-${tagType}`;
    tagSpan.textContent = tag;

    const bodySpan = document.createElement('span');
    bodySpan.className = 'log-body';
    bodySpan.textContent = message;

    entry.appendChild(timeSpan);
    entry.appendChild(tagSpan);
    entry.appendChild(bodySpan);

    traceLogContainer.appendChild(entry);
    traceLogContainer.scrollTop = traceLogContainer.scrollHeight;
  }

  function clearLogs() {
    traceLogContainer.innerHTML = '';
  }

  // Reset visual pipeline steps
  function resetPipelineSteps() {
    const steps = [
      { node: stepNode1, badge: stepBadge1, defaultText: 'IDLE' },
      { node: stepNode2, badge: stepBadge2, defaultText: 'IDLE' },
      { node: stepNode3, badge: stepBadge3, defaultText: 'IDLE' }
    ];

    steps.forEach(s => {
      s.node.className = 'pipeline-step step-idle';
      s.badge.className = 'step-status-tag';
      s.badge.textContent = s.defaultText;
    });
  }

  // Update pipeline step state
  function updateStep(stepIndex, status, label) {
    const map = [
      { node: stepNode1, badge: stepBadge1 },
      { node: stepNode2, badge: stepBadge2 },
      { node: stepNode3, badge: stepBadge3 }
    ];

    const target = map[stepIndex - 1];
    if (!target) return;

    target.node.className = `pipeline-step step-${status.toLowerCase()}`;
    target.badge.className = `step-status-tag badge-status badge-${status === 'passed' ? 'emerald' : status === 'paused' ? 'amber' : status === 'blocked' ? 'crimson' : 'cyan'}`;
    target.badge.textContent = label || status.toUpperCase();
  }

  // Update verdict badge in action bar
  function setVerdictBadge(verdict) {
    activeTraceVerdictEl.textContent = verdict;
    activeTraceVerdictEl.className = 'badge-status';

    if (verdict === 'PASSED' || verdict === 'ALLOWED') {
      activeTraceVerdictEl.classList.add('badge-emerald');
    } else if (verdict === 'PAUSED_HITL' || verdict === 'PENDING_APPROVAL') {
      activeTraceVerdictEl.classList.add('badge-amber');
    } else if (verdict === 'BLOCKED' || verdict === 'POLICY_VIOLATION' || verdict === 'SECURITY_BLOCK') {
      activeTraceVerdictEl.classList.add('badge-crimson');
    } else {
      activeTraceVerdictEl.classList.add('badge-cyan');
    }
  }

  // Update Raw JSON Trace
  function updateJsonOutput(data) {
    try {
      rawJsonOutput.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
      rawJsonOutput.textContent = String(data);
    }
  }

  // HITL Card State Manager
  function showHitlCard(trace) {
    activePendingHitlTrace = trace;
    hitlEmptyMsg.style.display = 'none';
    hitlActiveCard.style.display = 'block';

    hitlClaimId.textContent = trace.trace_id || 'TRC-HITL';
    hitlClaimEmp.textContent = trace.claim ? trace.claim.employee_id : 'EMP-UNKNOWN';
    hitlClaimAmount.textContent = trace.claim ? `$${Number(trace.claim.amount).toFixed(2)}` : '$0.00';
    hitlClaimRule.textContent = trace.policy_verdict?.rule || 'RULE #2 HITL_ESCALATION';

    hitlQueueCount.textContent = '1 PENDING';
    hitlQueueCount.className = 'badge-status badge-amber';
  }

  function hideHitlCard() {
    activePendingHitlTrace = null;
    hitlActiveCard.style.display = 'none';
    hitlEmptyMsg.style.display = 'block';

    hitlQueueCount.textContent = '0 PENDING';
    hitlQueueCount.className = 'badge-status badge-cyan';
  }

  // Health-check / ping backend
  async function checkBackendConnection() {
    try {
      const res = await fetch(`${BACKEND_URL}/api/claims/traces`, { method: 'GET' });
      if (res.ok) {
        isBackendLive = true;
        systemStatusDot.className = 'status-dot';
        systemStatusText.textContent = 'ENGINE: LIVE (PORT 8000)';
      } else {
        throw new Error('Non-200');
      }
    } catch (e) {
      isBackendLive = false;
      systemStatusDot.className = 'status-dot amber';
      systemStatusText.textContent = 'ENGINE: MOCK RESILIENCE LAYER';
    }
  }

  // Execute Claim Pipeline
  async function executeClaimSubmission(claimPayload) {
    btnSubmitClaim.disabled = true;
    clearLogs();
    resetPipelineSteps();
    hideHitlCard();

    enforcedChecksCounter++;
    metricChecksCount.textContent = String(enforcedChecksCounter);

    appendLog('CLAIM_IN', 'info', `Ingesting claim: ${claimPayload.employee_id} | ${claimPayload.vendor} | $${Number(claimPayload.amount).toFixed(2)} [${claimPayload.category}]`);
    appendLog('POLICY_SCAN', 'guard', `Executing deterministic pre-execution guardrail interceptor...`);

    let resultTrace = null;

    if (isBackendLive) {
      try {
        const response = await fetch(`${BACKEND_URL}/api/claims/run`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(claimPayload)
        });
        if (response.ok) {
          resultTrace = await response.json();
        } else {
          throw new Error(`Backend returned status ${response.status}`);
        }
      } catch (err) {
        appendLog('FAILOVER', 'guard', `Backend unavailable (${err.message}). Engaging mock fallback resilience engine.`);
        if (window.AegisMock) {
          resultTrace = window.AegisMock.runClaim(claimPayload);
        }
      }
    } else {
      if (window.AegisMock) {
        resultTrace = window.AegisMock.runClaim(claimPayload);
      }
    }

    if (!resultTrace) {
      appendLog('ERR_CRIT', 'block', 'System error: Unable to compute trace response.');
      btnSubmitClaim.disabled = false;
      return;
    }

    currentActiveTrace = resultTrace;
    renderTrace(resultTrace);
    btnSubmitClaim.disabled = false;
  }

  // Render Full Trace Execution
  function renderTrace(trace) {
    activeTraceIdEl.textContent = trace.trace_id || 'TRC-UNKNOWN';
    setVerdictBadge(trace.verdict || trace.status || 'UNKNOWN');
    activeTraceLatencyEl.textContent = `${trace.guardrail_latency_ms || '2.1'} ms`;
    metricLatency.textContent = `${trace.guardrail_latency_ms || '2.1'} ms`;

    updateJsonOutput(trace);

    // Render Steps in Visual Pipeline and Logs
    const steps = trace.steps || [];
    let completedStepsCount = 0;

    steps.forEach((step, idx) => {
      const stepNum = idx + 1;
      const stepName = step.name || (stepNum === 1 ? 'verify_vendor_tax_id' : stepNum === 2 ? 'check_department_budget' : 'execute_ledger_payout');

      if (step.status === 'PASSED') {
        completedStepsCount++;
        updateStep(stepNum, 'passed', 'VERIFIED');
        appendLog('TOOL_CALL', 'tool', `${stepName}() -> ${JSON.stringify(step.output || step.result || 'OK')}`);
      } else if (step.status === 'PAUSED_HITL' || step.status === 'PAUSED') {
        updateStep(stepNum, 'paused', 'HITL PAUSED');
        appendLog('INTERCEPT', 'guard', `[POLICY INTERCEPTION] ${stepName}() HALTED: ${trace.policy_verdict?.reason || 'Exceeds auto-approval limit ($500).'}`);
      } else if (step.status === 'BLOCKED' || step.status === 'VIOLATION') {
        updateStep(stepNum, 'blocked', 'BLOCKED');
        appendLog('POLICY_BLOCK', 'block', `[SECURITY VIOLATION] ${stepName}() TERMINATED: ${trace.policy_verdict?.reason || 'Policy check failed.'}`);
      }
    });

    activeTraceStepsEl.textContent = `${completedStepsCount} / 3`;

    // Handle Verdict Outcomes
    if (trace.verdict === 'PASSED' || trace.verdict === 'ALLOWED') {
      appendLog('SETTLED', 'pass', `Claim ${trace.trace_id} executed successfully and ledger transaction recorded.`);
    } else if (trace.verdict === 'PAUSED_HITL') {
      appendLog('HITL_QUEUE', 'guard', `Claim flagged for mandatory Human-in-the-Loop approval under Rule #2.`);
      showHitlCard(trace);
    } else if (trace.verdict === 'BLOCKED' || trace.verdict === 'POLICY_VIOLATION' || trace.verdict === 'SECURITY_BLOCK') {
      appendLog('ABORT', 'block', `Deterministic guardrail rejected transaction. Payout blocked fail-safe.`);
    }
  }

  // HITL Decision Handler (Approve / Reject)
  async function handleHitlDecision(decision) {
    if (!activePendingHitlTrace) return;

    const traceId = activePendingHitlTrace.trace_id;
    const reviewerNote = hitlReviewerNote.value || (decision === 'APPROVE' ? 'Approved by Operator' : 'Rejected by Operator');

    appendLog('HITL_ACTION', decision === 'APPROVE' ? 'pass' : 'block', `Human Operator dispatched decision: ${decision} (${reviewerNote})`);

    let responseTrace = null;

    if (isBackendLive) {
      try {
        const res = await fetch(`${BACKEND_URL}/api/claims/${traceId}/approve`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ decision, reviewer_note: reviewerNote })
        });
        if (res.ok) {
          responseTrace = await res.json();
        } else {
          throw new Error('Approval API returned status ' + res.status);
        }
      } catch (err) {
        appendLog('FAILOVER', 'guard', 'Approval API fallback engaged.');
        if (window.AegisMock) {
          responseTrace = window.AegisMock.approveClaim(traceId, decision, reviewerNote);
        }
      }
    } else {
      if (window.AegisMock) {
        responseTrace = window.AegisMock.approveClaim(traceId, decision, reviewerNote);
      }
    }

    if (responseTrace) {
      currentActiveTrace = responseTrace;
      renderTrace(responseTrace);
    }

    hideHitlCard();
  }

  // Event Listeners
  claimForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const payload = {
      employee_id: claimEmp.value.trim(),
      vendor: claimVendor.value.trim(),
      category: claimCategory.value,
      amount: parseFloat(claimAmount.value) || 0,
      notes: claimNotes.value.trim()
    };
    executeClaimSubmission(payload);
  });

  btnHitlApprove.addEventListener('click', () => handleHitlDecision('APPROVE'));
  btnHitlReject.addEventListener('click', () => handleHitlDecision('REJECT'));

  btnCopyJson.addEventListener('click', () => {
    navigator.clipboard.writeText(rawJsonOutput.textContent).then(() => {
      const orig = btnCopyJson.textContent;
      btnCopyJson.textContent = 'COPIED!';
      setTimeout(() => { btnCopyJson.textContent = orig; }, 1200);
    });
  });

  // Export functions to global scope for demo scenarios & test suite
  window.AegisApp = {
    executeClaimSubmission,
    appendLog,
    clearLogs,
    resetPipelineSteps,
    setVerdictBadge,
    updateJsonOutput,
    renderTrace,
    showHitlCard,
    hideHitlCard,
    checkBackendConnection,
    getBackendUrl: () => BACKEND_URL
  };

  // Initial connection check on page load
  checkBackendConnection();

})();
