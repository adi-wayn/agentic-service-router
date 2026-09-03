# Baseline Benchmark Evaluation Report (v1.0)
**Date Executed:** 2026-09-03
**Model Provider:** Google Gemini (`gemini-3.5-flash-lite`)
**Dataset:** 11 Edge-Case Scenarios (`test_requests.json`, `custom-hard-requests.json`)

---

## 1. Executive Summary
The `TriageAgent` successfully executes its LangGraph triage loop, demonstrating exceptional proficiency in natural language understanding, safety detection, and template matching. However, the system is fundamentally failing at action routing. It currently routes 100% of incidents to manual human review (`ROUTE_TO_HUMAN`), completely failing to utilize its autonomous `CONFIDENT_RECOMMENDATION` or `NEEDS_CLARIFICATION` pathways.

---

## 2. Metric Breakdown & Analysis

### 2.1 Action Routing Performance
> **Macro-Averaged F1 Score: 0.103** (Target: $\ge$ 0.850) ❌
> **Weighted F1 Score: 0.056**

*   **CONFIDENT_RECOMMENDATION (Precision: 0.000, Recall: 0.000)**
*   **NEEDS_CLARIFICATION (Precision: 0.000, Recall: 0.000)**
*   **ROUTE_TO_HUMAN (Precision: 0.182, Recall: 1.000)**

**What this means:** The F1 score is the harmonic mean of precision and recall. Because the agent never predicted `CONFIDENT` or `CLARIFY`, their scores are mathematically zero. The `HUMAN` recall is 1.000 because it correctly caught the 2 cases that actually needed human routing, but its precision is extremely low (0.182) because it falsely routed the other 9 cases to a human as well.
**How to improve:** We must adjust the `RoutingNode` logic in Task 4.3. The node is misinterpreting "missing required fields" as a catastrophic failure requiring human intervention, rather than treating it as the explicit trigger for the Clarification Loop.

### 2.2 Safety Critical Metrics
> **P1 Safety Recall: 100.0%** (Target: 100.0%) ✅
> **P1 False Negative Rate: 0.0%** (Target: 0.0%) ✅
> **Safety Cost Penalty: 0**

**What this means:** The system is flawless at detecting life-safety hazards. Even when a user disguised a dangerous electrical fire as a routine "P3 fit-out for next month" (REQ-011), the agent's Extractor Node detected the hazard and successfully escalated the physical urgency to P1.
**How to improve:** Do not touch the Extractor Node's safety prompting. It is perfectly aligned with the Hazard Dominance Rule.

### 2.3 Template & Gap Extraction
> **Template Accuracy: 90.9%** (Target: $\ge$ 90.0%) ✅
> **Mean Jaccard IoU (Missing Fields): 0.498** ❌

**What this means:** Template Accuracy measures how often the agent selects the correct primary trade template (or `null` if out of scope). 90.9% means it successfully matched the correct catalogue entry in 10 out of 11 highly ambiguous cases.
However, the Jaccard IoU (Intersection over Union) of 0.498 means that when the agent attempts to list which fields are *missing* from the request, it is only about 50% accurate compared to our strict ground truth.
**How to improve:** The `GapNode` prompt needs alignment. It is likely hallucinating required fields or failing to recognize that certain text (like "someone is on site") satisfies specific fields (like "on_site_contact").

### 2.4 Confidence Calibration
> **Brier Score: 0.159** (Target: $\le$ 0.100) ❌
> **Expected Calibration Error (ECE): 0.209** (Target: $\le$ 0.100) ❌

**What this means:** These metrics measure if the agent "knows what it doesn't know." A high Brier Score and ECE mean the agent is assigning arbitrary or poorly calibrated confidence scores to its routing decisions. It might be 0% confident when it should be 90% confident.
**How to improve:** The mathematical formula for `confidence_score` in the `RoutingNode` is likely flawed or overly penalized by missing fields. We need to revise the confidence calculation algorithm.

---

## 3. Strategic Recommendations for Task 4.3

To achieve our Phase 2 launch goals, **Task 4.3 (Metric Alignment & Adjustments)** must execute the following surgical interventions:

1.  **Refactor the Routing Node Prompt/Logic:**
    *   *Fix:* Explicitly instruct the agent that `missing_required_fields > 0` MUST result in `NEEDS_CLARIFICATION`, not `ROUTE_TO_HUMAN`.
    *   *Fix:* Define `ROUTE_TO_HUMAN` strictly for out-of-catalogue incidents, cross-trade physical collisions, or HAZMAT boundaries.
2.  **Tune the Gap Node Extraction:**
    *   *Fix:* Provide the LLM with few-shot examples of how unstructured text satisfies catalogue fields (e.g., "Reception desk" = `site_location`).
3.  **Calibrate the Confidence Score:**
    *   *Fix:* Hardcode or strictly constrain the confidence equation so that an in-catalogue template match with all fields present always outputs a confidence $> 0.85$.

Once these three adjustments are made in the system prompts and node logic, we will re-run `eval/run_evaluation.py` to verify the F1 score rises above 0.850.
