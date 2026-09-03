# Task 4.1: Evaluation Test Suite

## Overview
This task successfully built the mathematical evaluation foundation necessary to benchmark the Autonomous Service Request Router & Triage Agent against the SRS guidelines.

## Accomplishments
1. **Ground Truth Data Construction:**
   Created `data/eval_cases.json`, translating all 11 edge cases (REQ-001 to REQ-011) into a strict JSON schema. This file defines the `expected_template`, `expected_routing_action`, `expected_real_urgency`, and `expected_missing_fields` for each case. It correctly encodes the hard custom cases testing P1 override (REQ-011), hazard boundaries (REQ-010), and urgency escalation (REQ-009).

2. **Metric Math Formulation (`eval/metrics.py`):**
   Implemented robust pure-Python mathematical functions based exactly on the formulas defined in the SRS:
   *   `compute_confusion_matrix`: Processes multi-class accuracy, Precision, Recall, Macro-F1, and Weighted-F1 for routing actions.
   *   `compute_safety_metrics`: Isolates P1 emergency cases, calculating the critical P1 Hazard Sensitivity ($Rec_{P1}$ target = 100%), False Negative Rate, and the safety cost penalty metric.
   *   `compute_jaccard_iou`: Evaluates the Intersection over Union (IoU) of the missing intake gaps.
   *   `compute_calibration`: Calculates the Brier Score and Expected Calibration Error (ECE) for agent probabilistic confidence.

3. **Ground Truth Loader (`eval/ground_truth.py`):**
   Created typed `TestCase` classes and an `AssertionTracker` helper to decouple the testing dataset from the execution runner.

## Next Steps
In Task 4.2, we will build the asynchronous test runner to pump these 11 cases through the LangGraph agent and aggregate the results using these metric evaluators.
