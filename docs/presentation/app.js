/**
 * Field Services Intelligent Dispatcher (FS-ID)
 * Presentation & Technical White Paper Client Controller
 * Version: 2.0.0
 */

document.addEventListener('DOMContentLoaded', () => {
  initReadingProgressBar();
  initViewModeToggle();
  initNodeDrawers();
  initConfusionMatrix();
  initCaseStudyTabs();
  initDiffViewer();
  initMermaid();
});

/* 1. Reading Progress Bar */
function initReadingProgressBar() {
  const progressBar = document.getElementById('reading-progress');
  if (!progressBar) return;

  window.addEventListener('scroll', () => {
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = (window.scrollY / totalHeight) * 100;
    progressBar.style.width = `${Math.min(progress, 100)}%`;
  });
}

/* 2. View Mode Toggle (Executive Pitch Deck vs Technical White Paper) */
function initViewModeToggle() {
  const btnExec = document.getElementById('btn-mode-exec');
  const btnPaper = document.getElementById('btn-mode-paper');
  const body = document.body;

  if (!btnExec || !btnPaper) return;

  btnExec.addEventListener('click', () => {
    body.classList.remove('view-whitepaper');
    body.classList.add('view-executive');
    btnExec.classList.add('active');
    btnPaper.classList.remove('active');
  });

  btnPaper.addEventListener('click', () => {
    body.classList.remove('view-executive');
    body.classList.add('view-whitepaper');
    btnPaper.classList.add('active');
    btnExec.classList.remove('active');
  });
}

/* 3. Collapsible Node Drawers */
function initNodeDrawers() {
  const drawers = document.querySelectorAll('.node-drawer');
  drawers.forEach(drawer => {
    const header = drawer.querySelector('.node-drawer-header');
    if (!header) return;
    header.addEventListener('click', () => {
      drawer.classList.toggle('open');
    });
  });
}

/* 4. Interactive 3x3 Confusion Matrix */
const matrixCaseData = {
  'CONFIDENT-CONFIDENT': {
    title: 'True Positives: Confident Recommendations (2 Cases)',
    cases: ['REQ-001 (Server room AC heating fast)', 'REQ-011 (Basement electrical sparking & odor)'],
    explanation: 'Both high-urgency incidents with complete necessary intake parameters correctly received automated dispatch recommendations with 0.95+ confidence.'
  },
  'CONFIDENT-CLARIFY': {
    title: 'False Negatives: Expected Confident, got Clarify (0 Cases)',
    cases: [],
    explanation: 'Zero confident ground-truth cases were mistakenly trapped in clarification loops.'
  },
  'CONFIDENT-HUMAN': {
    title: 'False Negatives: Expected Confident, got Human (0 Cases)',
    cases: [],
    explanation: 'Zero confident ground-truth cases were prematurely escalated to human review.'
  },
  'CLARIFY-CONFIDENT': {
    title: 'False Positives: Expected Clarify, got Confident (0 Cases)',
    cases: [],
    explanation: 'The system never hallucinated missing fields or confidently dispatched incomplete tickets without verification.'
  },
  'CLARIFY-CLARIFY': {
    title: 'True Positives: Needs Clarification (6 Cases)',
    cases: ['REQ-002 (Kitchenette slow drip)', 'REQ-003 (Lights out & sparking charger)', 'REQ-004 (Undefined smoke alarm)', 'REQ-005 (Flooding pipe leak)', 'REQ-006 (Breaker panel trip)', 'REQ-008 (Quarterly filter maintenance)'],
    explanation: 'Correctly triggered bounded multi-turn clarification questions targeting missing locations or contact details.'
  },
  'CLARIFY-HUMAN': {
    title: 'False Negatives on Clarify: Escalated to Human (1 Case)',
    cases: ['REQ-009 (Broken magnetic badge reader lockout)'],
    explanation: 'REQ-009 was borderline between security lockout and general access maintenance. The margin collision detector safely favored human review.'
  },
  'HUMAN-CONFIDENT': {
    title: 'False Positives: Expected Human, got Confident (0 Cases)',
    cases: [],
    explanation: 'Zero hazardous or out-of-scope requests escaped to automated technician dispatch.'
  },
  'HUMAN-CLARIFY': {
    title: 'False Positives on Clarify: Expected Human (0 Cases)',
    cases: [],
    explanation: 'Zero out-of-catalogue requests wasted user time in futile clarification loops.'
  },
  'HUMAN-HUMAN': {
    title: 'True Positives: Route to Human (2 Cases)',
    cases: ['REQ-007 (Major structural office renovation)', 'REQ-010 (Suspected airborne asbestos contamination)'],
    explanation: 'Accurately detected out-of-catalogue boundaries and hazardous material risks, routing immediately to human facility managers.'
  }
};

function initConfusionMatrix() {
  const cells = document.querySelectorAll('.grid-cell[data-key]');
  const tooltipDisplay = document.getElementById('matrix-tooltip-display');
  if (!tooltipDisplay) return;

  cells.forEach(cell => {
    const key = cell.getAttribute('data-key');
    cell.addEventListener('mouseenter', () => {
      const data = matrixCaseData[key];
      if (data) {
        tooltipDisplay.innerHTML = `
          <strong style="color: var(--color-cyan);">${data.title}</strong><br>
          <span style="color: var(--text-primary);">${data.cases.length ? 'Identified Cases: ' + data.cases.join(', ') : 'None (Zero Cases)'}</span><br>
          <span style="color: var(--text-secondary); font-size: 0.8rem;">${data.explanation}</span>
        `;
      }
    });
  });
}

/* 5. Case Study Tabs */
const caseStudiesData = [
  {
    id: 1,
    title: 'Case 1: P1 Fire Hazard Override',
    template: 'ELEC_FAULT',
    urgency: 'P1 (Critical Hazard Escalation)',
    urgencyClass: 'badge-p1',
    action: 'CONFIDENT_RECOMMENDATION',
    actionClass: 'badge-confident',
    confidence: 98,
    rawText: '"No rush at all, but the electrical sub-panel in the basement server room is buzzing loudly, smells like scorched plastic, and sparks whenever the AC compressor turns on."',
    rationale: 'The ELEC_FAULT template was selected due to high-confidence matching of critical safety signals, specifically sparking and burning odors. The urgency was escalated from P3 to P1 under the Hazard Dominance Rule, as the reported symptoms indicate an active fire risk and potential for critical infrastructure failure. Stated polite sentiment ("no rush at all") was strictly decoupled from physical danger.',
    audit: 'ExtractorNode (detected fire/spark hazard -> P1) -> MatcherNode (ELEC_FAULT score: 0.98) -> GapNode (0 missing critical fields) -> RouterNode (C=0.98 >= 0.75 -> CONFIDENT) -> FinalizerNode (Rationale generated).'
  },
  {
    id: 2,
    title: 'Case 2: Incomplete Intake Clarification Loop',
    template: 'PLUMB_STD',
    urgency: 'P3 (Routine Maintenance)',
    urgencyClass: 'badge-p3',
    action: 'NEEDS_CLARIFICATION -> CONFIDENT',
    actionClass: 'badge-clarify',
    confidence: 75,
    rawText: '"One of the restroom sinks is constantly running and won\'t turn off completely, wasting water. On-site contact is Dave at 555-4321."',
    rationale: 'The PLUMB_STD template was selected because the reported issue of a running faucet is a routine maintenance task without active flooding. The initial intake lacked room location. Clarification loop asked: "Which restroom and floor is the faucet located on?" Requester replied: "2nd floor mens room near elevators". State merged, resolved in 1 turn.',
    audit: 'ExtractorNode -> MatcherNode (PLUMB_STD) -> GapNode (missing: site_location) -> RouterNode (C=0.55 -> CLARIFY) -> ClarifierNode (Gen Question) -> FeedbackNode (Ingest "2nd floor") -> ExtractorNode -> RouterNode (C=0.75 -> CONFIDENT).'
  },
  {
    id: 3,
    title: 'Case 3: Preventative Routine Dispatch',
    template: 'HVAC_MAINT',
    urgency: 'P3 (Standard Maintenance)',
    urgencyClass: 'badge-p3',
    action: 'CONFIDENT_RECOMMENDATION',
    actionClass: 'badge-confident',
    confidence: 95,
    rawText: '"Quarterly filter inspection and servicing needed for the rooftop condenser unit at Building B, 100 Innovation Parkway. Loading dock open 8am-4pm. Contact Sarah M. at ext 402."',
    rationale: 'The request was routed to the HVAC_MAINT template with a P3 urgency tier. This selection is justified by the explicit description of routine quarterly filter inspection and servicing, which lacks any indicators of equipment failure or safety hazards. All logistical and technical parameters were fully populated.',
    audit: 'ExtractorNode (no hazard -> P3) -> MatcherNode (HVAC_MAINT: 0.96) -> GapNode (0 missing fields) -> RouterNode (C=0.95 -> CONFIDENT) -> FinalizerNode.'
  },
  {
    id: 4,
    title: 'Case 4: Out-of-Catalogue Hazmat Escalation',
    template: 'null (Out-of-Scope)',
    urgency: 'P1 (Critical Hazard)',
    urgencyClass: 'badge-p1',
    action: 'ROUTE_TO_HUMAN',
    actionClass: 'badge-human',
    confidence: 10,
    rawText: '"Our workers were drilling into the east basement wall and hit old textured pipe insulation, releasing white powdery dust into the air. Work has stopped."',
    rationale: 'The request was routed to a human operator because it is out-of-catalogue. While the issue involves pipe insulation, the primary concern is a life-safety hazard (potential asbestos / hazardous particulate exposure) exceeding standard trade scope. Evaluated urgency was elevated to P1 due to airborne contaminants.',
    audit: 'ExtractorNode (asbestos / hazmat detected -> P1) -> MatcherNode (Max catalogue score: 0.22 < 0.50) -> GapNode -> RouterNode (out_of_catalogue=True -> C=0.10 -> ROUTE_TO_HUMAN) -> FinalizerNode.'
  },
  {
    id: 5,
    title: 'Case 5: Security Lockout Response',
    template: 'LOCK_ACCESS',
    urgency: 'P2 (Urgent Degradation)',
    urgencyClass: 'badge-p2',
    action: 'CONFIDENT_RECOMMENDATION',
    actionClass: 'badge-confident',
    confidence: 95,
    rawText: '"The magnetic badge reader on the exterior rear entrance door is completely unresponsive. The door is stuck locked from the outside, blocking employee entry from the parking lot."',
    rationale: 'The LOCK_ACCESS template was selected due to high signal alignment with the reported magnetic badge reader failure and exterior door lockout. The urgency was assigned as P2 because the failure represents a significant operational disruption to facility access without posing an immediate life-safety threat.',
    audit: 'ExtractorNode (access lockout -> P2) -> MatcherNode (LOCK_ACCESS: 0.95) -> GapNode (0 missing required) -> RouterNode (C=0.95 -> CONFIDENT) -> FinalizerNode.'
  }
];

function initCaseStudyTabs() {
  const tabNav = document.getElementById('case-tabs-nav');
  const titleEl = document.getElementById('case-title');
  const templateEl = document.getElementById('case-template');
  const urgencyEl = document.getElementById('case-urgency');
  const actionEl = document.getElementById('case-action');
  const confValEl = document.getElementById('case-conf-val');
  const confFillEl = document.getElementById('case-conf-fill');
  const rawTextEl = document.getElementById('case-raw-text');
  const rationaleEl = document.getElementById('case-rationale');
  const auditEl = document.getElementById('case-audit');

  if (!tabNav) return;

  function renderCase(idx) {
    const c = caseStudiesData[idx];
    if (!c) return;

    if (titleEl) titleEl.textContent = c.title;
    if (templateEl) templateEl.textContent = c.template;
    
    if (urgencyEl) {
      urgencyEl.textContent = c.urgency;
      urgencyEl.className = `badge ${c.urgencyClass}`;
    }
    
    if (actionEl) {
      actionEl.textContent = c.action;
      actionEl.className = `badge ${c.actionClass}`;
    }

    if (confValEl) confValEl.textContent = `${c.confidence}%`;
    if (confFillEl) {
      confFillEl.style.width = `${c.confidence}%`;
      confFillEl.className = `confidence-bar-fill ${c.confidence < 40 ? 'p1' : c.confidence < 75 ? 'p2' : ''}`;
    }

    if (rawTextEl) rawTextEl.textContent = c.rawText;
    if (rationaleEl) rationaleEl.textContent = c.rationale;
    if (auditEl) auditEl.textContent = c.audit;

    document.querySelectorAll('.case-tab-btn').forEach((btn, i) => {
      btn.classList.toggle('active', i === idx);
    });
  }

  caseStudiesData.forEach((c, i) => {
    const btn = document.createElement('button');
    btn.className = `case-tab-btn ${i === 0 ? 'active' : ''}`;
    btn.textContent = `Case ${c.id}: ${c.template}`;
    btn.addEventListener('click', () => renderCase(i));
    tabNav.appendChild(btn);
  });

  renderCase(0);
}

/* 6. Before/After Diff Viewer */
const diffData = {
  'REQ-002': {
    title: 'REQ-002: Restroom Tap Slow Drip (Kitchenette)',
    v1: `{
  "request_id": "REQ-002",
  "predicted_template": "PLUMB_STD",
  "routing_action": "ROUTE_TO_HUMAN",  <-- FAILURE: Over-penalized missing room
  "confidence_score": 0.28,             <-- FAILURE: Gap penalty collapsed confidence
  "missing_fields": [
    "site_location",
    "is_there_a_safety_risk",          <-- BUG: GapNode failed to map boolean
    "affected_circuits_or_area"        <-- BUG: Hallucinated electrical field
  ],
  "clarification_loop_triggered": false
}`,
    v2: `{
  "request_id": "REQ-002",
  "predicted_template": "PLUMB_STD",
  "routing_action": "NEEDS_CLARIFICATION", <-- SUCCESS: Bounded clarification
  "confidence_score": 0.55,                <-- CALIBRATED: Band [0.45, 0.70]
  "missing_fields": [
    "site_location"                        <-- CLEAN: Exactly matches ground truth
  ],
  "clarification_loop_triggered": true,
  "resolved_in_turns": 1                   <-- RESOLVED: Autonomous convergence
}`
  },
  'REQ-011': {
    title: 'REQ-011: Disguised Life-Safety Hazard (Basement sparking panel)',
    v1: `{
  "request_id": "REQ-011",
  "raw_text": "No rush at all, but basement panel is buzzing and smells scorched...",
  "assessed_urgency": "P3",             <-- CRITICAL VULNERABILITY: Polite phrasing masked hazard
  "routing_action": "ROUTE_TO_HUMAN",
  "confidence_score": 0.35,
  "safety_penalty": 100                 <-- FATAL: False Negative on Life Safety
}`,
    v2: `{
  "request_id": "REQ-011",
  "raw_text": "No rush at all, but basement panel is buzzing and smells scorched...",
  "assessed_urgency": "P1",             <-- HAZARD DOMINANCE: Sparks & scorch force P1
  "routing_action": "CONFIDENT_RECOMMENDATION",
  "confidence_score": 0.98,
  "safety_penalty": 0                   <-- PERFECT: 100% P1 Sensitivity maintained
}`
  }
};

function initDiffViewer() {
  const selector = document.getElementById('diff-case-select');
  const v1Code = document.getElementById('diff-v1-code');
  const v2Code = document.getElementById('diff-v2-code');
  const diffTitle = document.getElementById('diff-case-title');

  if (!selector || !v1Code || !v2Code) return;

  function updateDiff(key) {
    const item = diffData[key];
    if (!item) return;
    if (diffTitle) diffTitle.textContent = item.title;
    v1Code.textContent = item.v1;
    v2Code.textContent = item.v2;
  }

  selector.addEventListener('change', (e) => {
    updateDiff(e.target.value);
  });

  updateDiff('REQ-002');
}

/* 7. Mermaid Initializer */
function initMermaid() {
  if (typeof mermaid !== 'undefined') {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'dark',
      themeVariables: {
        darkMode: true,
        background: '#0b0f16',
        primaryColor: '#1f2937',
        primaryTextColor: '#f0f6fc',
        primaryBorderColor: '#388bfd',
        lineColor: '#58a6ff',
        secondaryColor: '#161b22',
        tertiaryColor: '#0d1117'
      },
      flowchart: {
        curve: 'basis',
        nodeSpacing: 40,
        rankSpacing: 40
      }
    });
  }
}
